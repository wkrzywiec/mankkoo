import pytest
import base64
import pathlib
import accounting.account as account
import numpy as np
from pandas._testing import assert_frame_equal
import accounting.data_for_test as td
import accounting.config as config


start_data = td.account_data([
    ['iban-1', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000, 'PLN', 1000],
    ['iban-1', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['iban-1', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.3, 'PLN', 774.48]
])

millenium_data = td.account_data(td.millenium_data)

end_data = td.account_data([
    ['iban-1', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000.00, 'PLN', 1000.00],
    ['iban-1', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['iban-1', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.30, 'PLN', 774.48],
    ['iban-1', '2021-03-15', 'Train ticket', 'Detail new', np.NaN, np.NaN, -100.00, 'PLN', 674.48],
    ['iban-1', '2021-03-16', 'Bus ticket', 'Detail new', np.NaN, np.NaN, -200.00, 'PLN', 474.48],
    ['iban-1', '2021-03-17', 'Salary', 'Detail new', np.NaN, np.NaN, 3000.33, 'PLN', 3474.81]
])


def test_add_new_operation_for_incorrect_bank(mocker):
    # GIVEN
    mocker.patch('accounting.config.load_user_config', side_effect=[td.user_config])

    # WHEN
    with pytest.raises(ValueError) as ex:
        account.add_new_operations('not known account', file_name='not_known_bank.csv')

    # THEN
    assert "Failed to load bank definition. There is no bank account definition with an id 'not known account'" in str(ex.value)

def test_add_new_operations_by_filename(mocker):
    # GIVEN
    mocker.patch('accounting.config.load_user_config', side_effect=[td.user_config])
    mocker.patch('accounting.importer.importer.load_bank_data', side_effect=[millenium_data])
    mocker.patch('accounting.database.load_accounts', side_effect=[start_data])
    mocker.patch('accounting.total.update_total_money')
    mocker.patch('accounting.total.update_monthly_profit')
    mocker.patch('pandas.DataFrame.to_csv')

    # WHEN
    df = account.add_new_operations('iban-1', file_name='test_pl_millenium.csv')

    # THEN
    assert_frame_equal(end_data, df)

def test_add_new_operations_by_contents(mocker):
    # GIVEN
    account_raw_data = open(str(pathlib.Path(__file__).parent.absolute()) + '/data/test_pl_millenium.csv', "r", encoding="utf8").read().encode('utf8')
    encoded_account = base64.b64encode(account_raw_data)

    mocker.patch('accounting.config.load_user_config', side_effect=[td.user_config])
    mocker.patch('accounting.importer.importer.load_bank_data', side_effect=[millenium_data])
    mocker.patch('accounting.database.load_accounts', side_effect=[start_data])
    mocker.patch('accounting.total.update_total_money')
    mocker.patch('accounting.total.update_monthly_profit')
    mocker.patch('pandas.DataFrame.to_csv')

    # WHEN
    df = account.add_new_operations('iban-1', contents='data:application/vnd.ms-excel;' + str(encoded_account))

    # THEN
    assert_frame_equal(end_data, df)

def test_add_new_operations_multiple_banks(mocker):
    # GIVEN
    start_data = td.account_data([
        ['iban-1', '2020-12-01', 'a', 'a', np.NaN, '', -1000, 'PLN', 2000],
        ['iban-1', '2021-01-01', 'a', 'a', np.NaN, '', 1000, 'PLN', 1000],
        ['iban-2', '2021-01-31', 'a', 'a', np.NaN, np.NaN, -222.22, 'PLN', 10]
    ])

    millenium = td.account_data([
        ['iban-1', '2021-02-15', 'Train ticket', 'Detail new', np.NaN, np.NaN, -500, 'PLN', np.NaN]
    ])

    mocker.patch('accounting.config.load_user_config', side_effect=[td.user_config])
    mocker.patch('accounting.importer.importer.load_bank_data', side_effect=[millenium])
    mocker.patch('accounting.database.load_accounts', side_effect=[start_data])
    mocker.patch('accounting.total.update_total_money')
    mocker.patch('accounting.total.update_monthly_profit')
    mocker.patch('pandas.DataFrame.to_csv')

    # WHEN
    df = account.add_new_operations('iban-1', file_name='test_pl_millenium.csv')

    # THEN
    millenium_balance = df.iloc[-1]['Balance']
    assert millenium_balance == 500
