import pytest
import os
import uuid
from datetime import datetime, timezone, timedelta
from testcontainers.postgres import PostgresContainer

import mankkoo.event_store as es
import mankkoo.database as db

postgres = PostgresContainer("postgres:16-alpine")
initPostgresContainer = False


@pytest.fixture(scope="module", autouse=True)
def setup(request):
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
    db.init_db()


@pytest.fixture(scope="function", autouse=True)
def setup_data():
    print("Cleaning database...")
    db.execute(
        "TRUNCATE events, streams;"
    )

# add multiple events
# Next event is saved in the event store if it has the succeeding version in the stream
# Next event is not saved in the event store if it has the same version as the latest event in the stream
# Next event is not saved in the event store if it has the same version as one of the events in the stream
# Next event is not saved in the event store if it has a version that skips couple versions in the stream

# Events are loaded from a store and are ordered by version
# 

def __test1():
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            (cid) = cur.fetchone()
            return cid


def test_add_new_event():
    assert __test1()[0] == 1
    # given
    
    stream_type = 'account'
    stream_id = uuid.uuid4()
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
    occured_at = datetime.now(timezone.utc) - timedelta(days=10)
    
    events = [
        es.Event(stream_type, stream_id, 'AccountOpened', accountOpenedData, occured_at),
        es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 2),
        es.Event(stream_type, stream_id, 'MoneyWithdrawn', moneyWithdrawnData, occured_at + timedelta(days=2), 3)
    ]
    
    # when
    es.store(events)

    # then
    
