import pytest
import copy
# from mankkoo.app import app
import mankkoo.data_for_test as td


def test_load_all_accounts(mocker, test_client):
    # GIVEN
    user_config = copy.deepcopy(td.user_config)
    mocker.patch('mankkoo.util.config.load_user_config', side_effect=[user_config, user_config])

    expected_account = td.user_config['accounts']['definitions'][0]

    # WHEN
    response = test_client.get('/api/accounts')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == 7

    assert payload[0]['active'] == expected_account['active']
    assert payload[0]['alias'] == expected_account['alias']
    assert payload[0]['bankName'] == expected_account['bank']
    assert payload[0]['bankUrl'] == expected_account['bank_url']
    assert payload[0]['id'] == expected_account['id']
    assert payload[0]['name'] == expected_account['name']
    assert payload[0]['type'] == expected_account['type']
    assert payload[0]['importer'] == expected_account['importer']


def test_load_all_operations(mocker, test_client):

    # GIVEN
    mocker.patch('mankkoo.account.account_db.load_all_operations_as_df', side_effect=[td.account_data(td.start_data)])
    mocker.patch('mankkoo.util.config.load_user_config', side_effect=[copy.deepcopy(td.user_config)])
    # expected_account = td.user_config['accounts']['definitions'][0].copy()

    # WHEN
    response = test_client.get('/api/accounts/operations')

    # THEN
    assert response.status_code == 200

    payload = response.get_json()
    assert len(payload) == len(td.start_data)

    # assert payload[0]['active'] == expected_account['active']
    # assert payload[0]['alias'] == expected_account['alias']
    # assert payload[0]['bankName'] == expected_account['bank']
    # assert payload[0]['bankUrl'] == expected_account['bank_url']
    # assert payload[0]['id'] == expected_account['id']
    # assert payload[0]['name'] == expected_account['name']
    # assert payload[0]['type'] == expected_account['type']
    # assert payload[0]['importer'] == expected_account['importer']
