import pytest
import os
from testcontainers.postgres import PostgresContainer

import mankkoo.database as db
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
        "TRUNCATE events, streams;"
    )


@pytest.fixture
def test_client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)

    return app
