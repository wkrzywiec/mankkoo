import pytest
import os
import uuid
from datetime import datetime, timezone, timedelta
from testcontainers.postgres import PostgresContainer

import mankkoo.event_store as es
import mankkoo.database as db

postgres = PostgresContainer("postgres:16-alpine")
initPostgresContainer = False

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


def test_add_new_events():
    # given
    events = [
        initEvent,
        es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 2),
        es.Event(stream_type, stream_id, 'MoneyWithdrawn', moneyWithdrawnData, occured_at + timedelta(days=2), 3)
    ]

    # when
    es.store(events)

    # then
    saved_events = __load_events(stream_id)
    assert len(saved_events) == 3
    assert events[0] == saved_events[0]


def test_event_is_not_stored_if_it_has_the_same_version_as_the_latest_event():
    # given
    es.store([initEvent])

    # when
    with pytest.raises(Exception):
        es.store([es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 1)])

    # then
    saved_events = __load_events(stream_id)
    assert len(saved_events) == 1


def test_event_is_not_stored_if_it_has_the_same_version_as_one_of_events():
    # given
    events = [
        initEvent,
        es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 2),
        es.Event(stream_type, stream_id, 'MoneyWithdrawn', moneyWithdrawnData, occured_at + timedelta(days=2), 3)
    ]

    es.store(events)

    # when
    with pytest.raises(Exception):
        es.store([es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 2)])

    # then
    saved_events = __load_events(stream_id)
    assert len(saved_events) == 3


def test_event_is_not_stored_if_it_skips_couple_versions():
    # given
    es.store([ initEvent ])

    # when
    with pytest.raises(Exception):
        es.store([es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 8)])

    # then
    saved_events = __load_events(stream_id)
    assert len(saved_events) == 1


def test_load_events():
    # given
    events = [
        initEvent,
        es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 2),
        es.Event(stream_type, stream_id, 'MoneyWithdrawn', moneyWithdrawnData, occured_at + timedelta(days=2), 3)
    ]

    es.store(events)

    # when
    saved_events = es.load(stream_id)

    # then
    assert len(saved_events) == 3
    assert events[0] == saved_events[0]


def test_udpate_streams_empty_metadata():
    # given
    es.store([ initEvent ])

    # when
    metadata = {"name": "bank", "number": 1234, "isActive": True}
    es.update_stream_metadata(stream_id, metadata)

    # then
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT metadata from streams WHERE id = '" + str(stream_id) + "'")
            (stored_metadata, ) = cur.fetchone()

    stored_metadata == metadata


def test_udpate_streams_filled_metadata():
    # given
    es.store([ initEvent ])
    es.update_stream_metadata(stream_id, metadata={"name": "bank", "number": 1234, "isActive": True})

    # when
    new_metadata = {"name": "something new"}
    es.update_stream_metadata(stream_id, new_metadata)

    # then
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT metadata from streams WHERE id = '" + str(stream_id) + "'")
            (stored_metadata, ) = cur.fetchone()

    stored_metadata == new_metadata


def __load_events(stream_id: uuid.UUID) -> list[es.Event]:
    result = []

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, stream_id, type, data, version, occured_at from events WHERE stream_id = '" + str(stream_id) + "' ORDER BY version")
            rows = cur.fetchall()

            for row in rows:
                print(row)
                result.append(
                    es.Event(event_id=uuid.UUID(row[0]), stream_id=uuid.UUID(row[1]), event_type=row[2], data=row[3], version=row[4], occured_at=row[5], stream_type="account")
                )

    return result
