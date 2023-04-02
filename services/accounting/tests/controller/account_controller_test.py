import pytest
from accounting.app import app
import accounting.data_for_test as td

def test_load_all_accounts(mocker):

    mocker.patch('accounting.util.config.load_user_config', side_effect=[td.user_config])
    expected_account = td.user_config['accounts']['definitions'][0].copy()
    
    response = app.test_client().get('/api/accounts')
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