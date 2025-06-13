import json
import uuid

from datetime import datetime, timedelta, timezone

import mankkoo.event_store as es


def test_stream_is_created__if_type_is_provided(test_client):
    # GIVEN
    data = {
        'type': 'account'
    }

    # WHEN
    response = test_client.post('/api/streams', data=json.dumps(data), headers=__headers())

    # THEN
    assert response.status_code == 201

    payload = response.get_json()
    assert payload['id'] is not None


def test_stream_is_created__if_type_and_metadata_are_provided(test_client):
    # GIVEN
    data = {
        'type': 'investment',
        'metadata': {
            'text': 'something',
            'number': 123,
            'bool': True
        }
    }

    # WHEN
    response = test_client.post('/api/streams', data=json.dumps(data), headers=__headers())

    # THEN
    assert response.status_code == 201

    payload = response.get_json()
    stream_id = payload['id']

    stream = es.get_stream_by_id(stream_id)
    assert stream.id == uuid.UUID(stream_id)
    assert stream.type == 'investment'
    assert stream.metadata == data['metadata']


def test_stream_is_not_created__if_type_is_not_provided(test_client):
    # GIVEN
    data = {
        'metadata': {
            'text': 'something'
        }
    }

    # WHEN
    response = test_client.post('/api/streams', data=json.dumps(data), headers=__headers())

    # THEN
    assert response.status_code == 422


def test_stream_is_not_created__if_invalid_type_is_provided(test_client):
    # GIVEN
    data = {
        'type': 'invalid'
    }

    # WHEN
    response = test_client.post('/api/streams', data=json.dumps(data), headers=__headers())

    # THEN
    assert response.status_code == 400


def test_all_streams_are_listed__if_no_filters_are_provided__and_stream_names_are_correctly_set(test_client):
    # GIVEN
    streams = [
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'investment', 0,
                  {"active": True, "category": "treasury_bonds", "bankName": "Bank B", "investmentName": "2 years Treasury Bonds"}),
        es.Stream(uuid.uuid4(), 'retirement', 0,
                  {"active": True, "alias": "PPK", "bank": "Bank PPK", "bankUrl": "https://www.ppk.com", "accountNumber": "ppk-bank-acc-11", "accountName": "'PPK", "accountType": "retirement", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'stocks', 0,
                  {"active": True, "type": "ETF", "broker": "Bank A", "etfUrl": "https://atlasetf.pl/etf-details/IE00B4L5Y983", "etfName": "ETF name", })
    ]
    es.create(streams)

    # WHEN
    response = test_client.get('/api/streams')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 4

    account_stream = next(x for x in payload if x['id'] == str(streams[0].id))
    assert account_stream['type'] == 'checking'
    assert account_stream['name'] == streams[0].metadata['bankName'] + ' - ' + streams[0].metadata['alias']

    investment_stream = next(x for x in payload if x['id'] == str(streams[1].id))
    assert investment_stream['type'] == 'treasury_bonds'
    assert investment_stream['name'] == streams[1].metadata['investmentName']

    retirement_stream = next(x for x in payload if x['id'] == str(streams[2].id))
    assert retirement_stream['type'] == 'retirement'
    assert retirement_stream['name'] == streams[2].metadata['alias']

    etf_stream = next(x for x in payload if x['id'] == str(streams[3].id))
    assert etf_stream['type'] == 'ETF'
    assert etf_stream['name'] == streams[3].metadata['etfName']


def test_only_active_streams_are_listed__if_active_qparam_equals_true(test_client):
    # GIVEN
    streams = [
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": False, "alias": "Bank account B", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-2", "accountName": "Super Personal account 2", "accountType": "checking", "importer": "MANKKOO"}),
    ]
    es.create(streams)

    # WHEN
    response = test_client.get('/api/streams?active=true')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 1

    assert payload[0]['id'] == str(streams[0].id)


def test_only_inactive_streams_are_listed__if_active_qparam_equals_false(test_client):
    # GIVEN
    streams = [
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": False, "alias": "Bank account B", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-2", "accountName": "Super Personal account 2", "accountType": "checking", "importer": "MANKKOO"}),
    ]
    es.create(streams)

    # WHEN
    response = test_client.get('/api/streams?active=false')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 1

    assert payload[0]['id'] == str(streams[1].id)


def test_only_accounts_streams_are_listed__if_type_qparam_equals_account(test_client):
    # GIVEN
    streams = [
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'investment', 0,
                  {"active": True, "category": "treasury_bonds", "bankName": "Bank B", "investmentName": "2 years Treasury Bonds"}),
    ]
    es.create(streams)

    # WHEN
    response = test_client.get('/api/streams?type=account')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 1

    assert payload[0]['id'] == str(streams[0].id)


def test_only_inactive_investment_streams_are_listed__if_type_qparam_equals_investment_and_active_qparam_is_false(test_client):
    # GIVEN
    streams = [
        es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"}),
        es.Stream(uuid.uuid4(), 'investment', 0,
                  {"active": True, "category": "treasury_bonds", "bankName": "Bank B", "investmentName": "2 years Treasury Bonds"}),
         es.Stream(uuid.uuid4(), 'investment', 0,
                  {"active": False, "category": "treasury_bonds", "bankName": "Bank B", "investmentName": "1 year Treasury Bonds"}),
    ]
    es.create(streams)

    # WHEN
    response = test_client.get('/api/streams?type=investment&active=false')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 1

    assert payload[0]['id'] == str(streams[2].id)


def test_stream_is_loaded(test_client):
    # GIVEN
    stream = es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"},
                  {"wallet": "Risky Investments"})
    es.create([stream])

    # WHEN
    response = test_client.get('/api/streams/' + str(stream.id))

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['type'] == 'account'
    assert payload['id'] == str(stream.id)


def test_stream_is_not_loaded__if_invalid_id_provided(test_client):
    # GIVEN
    stream = es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"})
    es.create([stream])

    invalid_uuid = 'c722f508-49b0-4d89-955e-f85322dffcb8'

    # WHEN
    response = test_client.get('/api/streams/' + invalid_uuid)

    # THEN
    assert response.status_code == 404


def test_events_are_added_to_stream(test_client):
    stream = es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"})
    es.create([stream])

    data = {
        "type": "AccountOpened",
        "data": {
            "stringType": "abc",
            "boolType": True,
            "numericType": 123
        },
        "occuredAt": "2019-08-24",
        "version": 1
    }

    # WHEN
    response = test_client.post(f'/api/streams/{stream.id}/events', data=json.dumps(data), headers=__headers())

    # THEN
    assert response.status_code == 201

    payload = response.get_json()
    assert payload['id'] is not None
    assert payload['version'] == 1


def test_events_are_not_added_to_stream__if_invalid_stream_id_was_provided(test_client):
    stream = es.Stream(uuid.uuid4(), 'account', 0,
                  {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"})
    es.create([stream])

    invalid_uuid = 'c722f508-49b0-4d89-955e-f85322dffcb8'

    data = {
        "type": "AccountOpened",
        "data": {},
        "occuredAt": "2019-08-24",
        "version": 1
    }

    # WHEN
    response = test_client.post(f'/api/streams/{invalid_uuid}/events', data=json.dumps(data), headers=__headers())

    # THEN
    assert response.status_code == 404


def test_events_are_loaded_for_stream(test_client):
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

    # WHEN
    response = test_client.get(f'/api/streams/{stream_id}/events')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 3

    assert payload[0]['type'] == 'MoneyWithdrawn'
    assert payload[0]['version'] == 3
    assert payload[0]['occuredAt'] == account_with_two_operations[2].occured_at.strftime('%Y-%m-%d')
    assert payload[0]['addedAt'] == datetime.now().strftime('%Y-%m-%d')
    assert payload[0]['data'] == moneyWithdrawnData

    assert payload[1]['type'] == 'MoneyDeposited'
    assert payload[1]['version'] == 2

    assert payload[2]['type'] == 'AccountOpened'
    assert payload[2]['version'] == 1


def test_stream_metadata_are_updated(test_client):
    # GIVEN
    stream = es.Stream(uuid.uuid4(), 'account', 0,
                {"active": True, "alias": "Bank account A", "bankName": "Bank A", "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1", "accountName": "Super Personal account", "accountType": "checking", "importer": "MANKKOO"})
    es.create([stream])

    metadata = {
        "strField": "abc",
        "boolField": True,
        "numericField": 123
    }

    # WHEN
    response = test_client.patch(f'/api/streams/{stream.id}', data=json.dumps({'metadata': metadata}), headers=__headers())

    # THEN
    assert response.status_code == 200
    stored_stream = es.get_stream_by_id(stream.id)
    assert stored_stream.metadata == metadata


def __headers():
    mimetype = 'application/json'
    return {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
