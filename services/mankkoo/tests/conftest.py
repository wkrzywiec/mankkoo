import pytest
import os
import uuid

from datetime import datetime, timezone, timedelta
from testcontainers.postgres import PostgresContainer

import mankkoo.database as db
import mankkoo.event_store as es
from mankkoo.app import create_app
from mankkoo.config import TestConfig

postgres = PostgresContainer("postgres:16-alpine")
initPostgresContainer = True


@pytest.fixture(scope="session", autouse=True)
def setup(request):
    os.environ["FLASK_ENV"] = "test"

    if initPostgresContainer:
        print('Starting PostgreSQL testcontainer...')
        postgres.start()

        def remove_container():
            postgres.stop()

        request.addfinalizer(remove_container)
        os.environ["DB_CONN"] = postgres.get_connection_url()
        os.environ["DB_HOST"] = postgres.get_container_host_ip()
        os.environ["DB_PORT"] = postgres.get_exposed_port(5432)
        os.environ["DB_USERNAME"] = postgres.username
        os.environ["DB_PASSWORD"] = postgres.password
        os.environ["DB_NAME"] = postgres.dbname

        print(f'Testcontainers postgres connection: {postgres.get_connection_url()}')
    else:
        print("Using local PostgreSQL instance for tests...")
        os.environ["DB_NAME"] = 'test'
    db.init_db()


@pytest.fixture(scope="function", autouse=True)
def setup_data():
    print("Cleaning database...")
    db.execute(
        "TRUNCATE events, streams, views;"
    )


@pytest.fixture
def test_client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture
def account_with_two_operations():

    stream_type = 'account'
    stream_id = uuid.uuid4()
    occured_at = datetime.now(timezone.utc) - timedelta(days=10)

    accountOpenedData = {
        "balance": 0.00,
        "number": "PL1234567890",
        "isActive": True,
        "openedAt": "2017-08-15 21:05:15.723336-07"
    }

    moneyDepositedData = {
        "amount": 100.00,
        "balance": 100.00
    }

    moneyWithdrawnData = {
        "amount": 50.50,
        "balance": 49.50
    }

    initEvent = es.Event(stream_type, stream_id, 'AccountOpened', accountOpenedData, occured_at)

    return [
        initEvent,
        es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 2),
        es.Event(stream_type, stream_id, 'MoneyWithdrawn', moneyWithdrawnData, occured_at + timedelta(days=2), 3)
    ]
