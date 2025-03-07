from datetime import datetime, timezone, timedelta

import uuid
import mankkoo.event_store as es


def test_all_accounts_are_loaded(test_client):
    # GIVEN
    streams = [
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Saving account", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-11", "accountName": "'Super Savings account", "accountType": "savigs", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'retirement', 0,
                  {"active": True, "alias": "PPK", "bank": "Bank PPK", "bankUrl": "https://www.ppk.com", "accountNumber": "ppk-bank-acc-11", "accountName": "'PPK", "accountType": "retirement", "importer": "MANKKOO"})
    ]
    es.create(streams)

    # WHEN
    response = test_client.get('/api/accounts')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 2

    first_account = next(x for x in payload if x['id'] == str(streams[0].id))
    assert first_account['active'] is True
    assert first_account['alias'] == streams[0].metadata['alias']
    assert first_account['bankName'] == streams[0].metadata['bankName']
    assert first_account['bankUrl'] == streams[0].metadata['bankUrl']
    assert first_account['number'] == streams[0].metadata['accountNumber']
    assert first_account['name'] == streams[0].metadata['accountName']
    assert first_account['type'] == streams[0].metadata['accountType']
    assert first_account['importer'] == streams[0].metadata['importer']


def test_all_account_operations_are_laoded__if_valid_account_id_is_provided(test_client, account_with_two_operations):
    # GIVEN
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

    account_with_two_operations = [
        es.Event(stream_type, stream_id, 'AccountOpened', accountOpenedData, occured_at),
        es.Event(stream_type, stream_id, 'MoneyDeposited', moneyDepositedData, occured_at + timedelta(days=1), 2),
        es.Event(stream_type, stream_id, 'MoneyWithdrawn', moneyWithdrawnData, occured_at + timedelta(days=2), 3)
    ]

    es.store(account_with_two_operations)
    stream_id = account_with_two_operations[0].stream_id

    # WHEN
    response = test_client.get(f'/api/accounts/{stream_id}/operations')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == len(account_with_two_operations)
