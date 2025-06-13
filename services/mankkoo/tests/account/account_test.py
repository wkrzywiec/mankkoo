import datetime
import pathlib
import time
import uuid

import pytest

import mankkoo.account.account as account
import mankkoo.account.account_db as account_db
import mankkoo.app as app
import mankkoo.data_for_test as td
import mankkoo.database as db
import mankkoo.event_store as es
from mankkoo.account.models import Bank

account_operations_raw_data = (
    open(
        str(pathlib.Path(__file__).parent.absolute()) + "/data/test_pl_millenium.csv",
        "r",
        encoding="utf8",
    )
    .read()
    .encode("utf8")
)


def test_new_operations_are_added_to_event_store(mocker):
    # GIVEN
    account_stream = td.any_account_stream()
    account_id = account_stream.id
    es.create([account_stream])

    mocker.patch(
        "mankkoo.account.account_db.get_bank_type", side_effect=[Bank.PL_MILLENIUM]
    )

    # WHEN
    account.add_new_operations(account_id, contents=account_operations_raw_data)

    # THEN
    events = __load_events(account_id)

    assert len(events) == 6

    assert events[0].event_type == "MoneyDeposited"
    assert events[0].version == 1
    assert events[0].occured_at == datetime.datetime(
        2021, 1, 1, tzinfo=datetime.timezone.utc
    )
    assert events[0].data == {
        "amount": 1000.0,
        "balance": 1000.0,
        "currency": "PLN",
        "title": "Jane Doe - Init money",
    }

    assert events[1].event_type == "MoneyWithdrawn"
    assert events[1].version == 2
    assert events[1].occured_at == datetime.datetime(
        2021, 2, 2, tzinfo=datetime.timezone.utc
    )
    assert events[1].data == {
        "amount": -200.0,
        "balance": 800.0,
        "currency": "PLN",
        "title": "Pizzeria - Out 1",
    }


def __load_events(stream_id: uuid.UUID) -> list[es.Event]:
    result = []

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, stream_id, type, data, version, occured_at FROM events WHERE stream_id = '{str(stream_id)}' ORDER BY version"
            )
            rows = cur.fetchall()

            for row in rows:
                print(row)
                result.append(
                    es.Event(
                        event_id=uuid.UUID(row[0]),
                        stream_id=uuid.UUID(row[1]),
                        event_type=row[2],
                        data=row[3],
                        version=row[4],
                        occured_at=row[5],
                        stream_type="account",
                    )
                )

    return result


def test_new_operations_are_added_and_balance_is_calculated(mocker):
    # GIVEN
    account_stream = td.any_account_stream()
    account_id = account_stream.id
    es.create([account_stream])

    mocker.patch(
        "mankkoo.account.account_db.get_bank_type", side_effect=[Bank.PL_MILLENIUM]
    )

    # WHEN
    account.add_new_operations(account_id, contents=account_operations_raw_data)

    # THEN
    assert es.get_stream_by_id(account_id).version == 6

    operations = account_db.load_operations_for_account(account_id)
    operations.reverse()

    assert len(operations) == 6

    assert float(operations[0].operation) == 1000.00
    assert operations[0].title == "Jane Doe - Init money"
    assert float(operations[0].balance) == 1000.00
    assert operations[0].currency == "PLN"

    assert float(operations[1].operation) == -200.00
    assert operations[1].title == "Pizzeria - Out 1"
    assert float(operations[1].balance) == 800.00

    assert float(operations[2].operation) == -3.33
    assert float(operations[2].balance) == 796.67


def test_new_operations_are_added_and_views_are_updated(mocker):
    # GIVEN
    account_stream = td.any_account_stream()
    account_id = account_stream.id
    es.create([account_stream])

    mocker.patch(
        "mankkoo.account.account_db.get_bank_type", side_effect=[Bank.PL_MILLENIUM]
    )

    app.start_listener_thread()

    # WHEN
    account.add_new_operations(account_id, contents=account_operations_raw_data)

    # THEN
    def all_views_are_created():
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM views")
                (views_count,) = cur.fetchone()
        print(f"Found {views_count} views")
        return views_count == 3

    __wait_for_condition(condition_func=all_views_are_created, timeout=10, interval=1)


def __wait_for_condition(condition_func, timeout=10, interval=1):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    raise TimeoutError(f"Condition was not met within {timeout} seconds.")


def test_new_operations_are_added_to_a_correct_stream_only(mocker):
    # GIVEN
    account_stream = td.any_account_stream()
    another_account_stream = td.any_account_stream()
    es.create([account_stream, another_account_stream])

    mocker.patch(
        "mankkoo.account.account_db.get_bank_type", side_effect=[Bank.PL_MILLENIUM]
    )

    # WHEN
    account.add_new_operations(account_stream.id, contents=account_operations_raw_data)

    # THEN
    assert es.get_stream_by_id(account_stream.id).version == 6
    assert es.get_stream_by_id(another_account_stream.id).version == 0


def test_new_operations_are_not_added_if_incorrect_invalid_account_id_is_provided():
    # GIVEN
    invalid_account_id = "14490940-640f-4f23-8468-af18411ab5f5"

    # WHEN
    with pytest.raises(ValueError) as ex:
        account.add_new_operations(invalid_account_id, file_name="not_known_bank.csv")

    # THEN
    assert (
        f"Failed to load bank definition. There is no bank account definition with an id '{invalid_account_id}'"
        in str(ex.value)
    )


def test_new_operations_are_not_added_if_a_stream_is_not_of_account_type(mocker):
    # GIVEN
    none_account_stream = td.any_stream("stocks")
    es.create([none_account_stream])

    # WHEN
    with pytest.raises(ValueError) as ex:
        account.add_new_operations(
            none_account_stream.id, contents=account_operations_raw_data
        )

    # THEN
    assert (
        f"Failed to load bank definition. There is no bank account definition with an id '{none_account_stream.id}'"
        in str(ex.value)
    )
