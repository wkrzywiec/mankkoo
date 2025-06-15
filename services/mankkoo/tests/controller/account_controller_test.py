import uuid
from datetime import datetime, timedelta, timezone

import mankkoo.event_store as es


def test_all_accounts_are_loaded(test_client):
    # GIVEN
    streams = [
        es.Stream(
            uuid.uuid4(),
            "account",
            "checking",
            "Super Personal account",
            "Bank A",
            True,
            0,
            {
                "alias": "Bank account A",
                "bankUrl": "https://www.bank-a.com",
                "accountNumber": "iban-1",
                "importer": "MANKKOO",
            },
        ),
        es.Stream(
            uuid.uuid4(),
            "account",
            "savings",
            "Super Savings account",
            "Bank A",
            True,
            0,
            {
                "alias": "Saving account",
                "bankUrl": "https://www.bank-a.com",
                "accountNumber": "iban-11",
                "importer": "MANKKOO",
            },
        ),
        es.Stream(
            uuid.uuid4(),
            "retirement",
            "retirement",
            "PPK",
            "Bank PPK",
            True,
            0,
            {
                "alias": "PPK",
                "bankUrl": "https://www.ppk.com",
                "accountNumber": "ppk-bank-acc-11",
                "importer": "MANKKOO",
            },
        ),
    ]
    es.create(streams)

    # WHEN
    response = test_client.get("/api/accounts")

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 2

    first_account = next(x for x in payload if x["id"] == str(streams[0].id))
    assert first_account["active"] is True
    assert first_account["alias"] == streams[0].metadata["alias"]
    assert first_account["bankName"] == streams[0].bank
    assert first_account["bankUrl"] == streams[0].metadata["bankUrl"]
    assert first_account["number"] == streams[0].metadata["accountNumber"]
    assert first_account["name"] == streams[0].name
    assert first_account["type"] == streams[0].subtype
    assert first_account["importer"] == streams[0].metadata["importer"]


def test_all_account_operations_are_laoded__if_valid_account_id_is_provided(
    test_client, account_with_two_operations
):
    # GIVEN
    stream_type = "account"
    stream_id = uuid.uuid4()
    occured_at = datetime.now(timezone.utc) - timedelta(days=10)

    accountOpenedData = {
        "balance": 0.00,
        "number": "PL1234567890",
        "isActive": True,
        "openedAt": "2017-08-15 21:05:15.723336-07",
    }

    moneyDepositedData = {"amount": 100.00, "balance": 100.00}

    moneyWithdrawnData = {"amount": 50.50, "balance": 49.50}

    account_with_two_operations = [
        es.Event(
            stream_type, stream_id, "AccountOpened", accountOpenedData, occured_at
        ),
        es.Event(
            stream_type,
            stream_id,
            "MoneyDeposited",
            moneyDepositedData,
            occured_at + timedelta(days=1),
            2,
        ),
        es.Event(
            stream_type,
            stream_id,
            "MoneyWithdrawn",
            moneyWithdrawnData,
            occured_at + timedelta(days=2),
            3,
        ),
    ]

    es.store(account_with_two_operations)
    stream_id = account_with_two_operations[0].stream_id

    # WHEN
    response = test_client.get(f"/api/accounts/{stream_id}/operations")

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == len(account_with_two_operations)
