import pytest
import scripts.main.data as data
import scripts.main.models as models
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal
import scripts.main.data_for_test as td


start_data = td.account_data([
    ['Millenium', 'checking', '360', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000, 'PLN', 1000],
    ['Millenium', 'checking', '360', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['Millenium', 'checking', '360', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.3, 'PLN', 774.48]
])

millenium_data = td.account_data(td.millenium_data)

end_data = td.account_data([
    ['Millenium', 'checking', '360', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000.00, 'PLN', 1000.00],
    ['Millenium', 'checking', '360', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['Millenium', 'checking', '360', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.30, 'PLN', 774.48],
    ['Millenium', 'checking', '360', '2021-03-15', 'Train ticket', 'Detail new', np.NaN, np.NaN, -100.00, 'PLN', 674.48],
    ['Millenium', 'checking', '360', '2021-03-16', 'Bus ticket', 'Detail new', np.NaN, np.NaN, -200.00, 'PLN', 474.48],
    ['Millenium', 'checking', '360', '2021-03-17', 'Salary', 'Detail new', np.NaN, np.NaN, 3000.33, 'PLN', 3474.81]
])


def test_add_new_operation_for_incorrect_bank():
    # GIVEN
    bank = 'NOT KNOWN BANK'

    # WHEN
    with pytest.raises(KeyError) as ex:
        data.add_new_operations(bank, 'not_known_bank.csv', 'not known account')

    # THEN
    assert 'Failed to load data from file. Not known bank. Was provided {} bank'.format(bank) in str(ex.value)

def test_add_new_operations(mocker):
    # GIVEN
    bank = models.Bank.PL_MILLENIUM

    mocker.patch('scripts.main.importer.importer.load_data', side_effect=[millenium_data, start_data])
    mocker.patch('scripts.main.total.update_total_money')
    mocker.patch('pandas.DataFrame.to_csv')

    # WHEN
    df = data.add_new_operations(bank, 'test_pl_millenium.csv', '360')

    # THEN
    assert_frame_equal(end_data, df)

def test_add_new_operations_multiple_banks(mocker):
    # GIVEN
    bank = models.Bank.PL_MILLENIUM

    account = td.account_data([
        ['Millenium', 'checking', '360', '2020-12-01', 'a', 'a', np.NaN, '', -1000, 'PLN', 2000],
        ['Millenium', 'checking', '360', '2021-01-01', 'a', 'a', np.NaN, '', 1000, 'PLN', 1000],
        ['ING', 'checking', 'Direct', '2021-01-31', 'a', 'a', np.NaN, np.NaN, -222.22, 'PLN', 10]
    ])

    millenium = td.account_data([
        ['Millenium', 'checking', '360', '2021-02-15', 'Train ticket', 'Detail new', np.NaN, np.NaN, -500, 'PLN', np.NaN]
    ])

    mocker.patch('scripts.main.importer.importer.load_data', side_effect=[millenium, account])
    mocker.patch('scripts.main.total.update_total_money')
    mocker.patch('pandas.DataFrame.to_csv')

    # WHEN
    df = data.add_new_operations(bank, 'test_pl_millenium.csv', '360')

    # THEN
    millenium_balance = df.iloc[-1]['Balance']
    assert millenium_balance == 500
