import json
import uuid
import mankkoo.database as db
import mankkoo.event_store as es


def test_load_all_accounts(test_client):
    # GIVEN
    streams = [
        es.Stream(uuid.uuid4(), 'account', 1,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'account', 1,
                  {"active": True, "alias": "Saving account", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-11", "accountName": "'Super Savings account", "accountType": "savigs", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'retirement', 1,
                  {"active": True, "alias": "PPK", "bank": "Bank PPK", "bankUrl": "https://www.ppk.com", "accountNumber": "ppk-bank-acc-11", "accountName": "'PPK", "accountType": "retirement", "importer": "MANKKOO"})
    ]
    __store_streams(streams)

    # WHEN
    response = test_client.get('/api/accounts')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    print(type(payload))
    print(type(payload[0]))
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


def __store_streams(streams: list[es.Stream]):
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            for stream in streams:
                cur.execute(
                    "INSERT INTO streams (id, type, version, metadata) VALUES (%s, %s, %s, %s)",
                    (str(stream.id), stream.type, stream.version, json.dumps(stream.metadata)))
            conn.commit()


def test_load_all_operations(test_client, account_with_two_operations):
    # GIVEN
    es.store(account_with_two_operations)
    stream_id = account_with_two_operations[0].stream_id

    # WHEN
    response = test_client.get(f'/api/accounts/{stream_id}/operations')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == len(account_with_two_operations)
