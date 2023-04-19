import pytest
import pathlib
import mankkoo.account.importer.importer as importer
import mankkoo.account.models as models
import mankkoo.data_for_test as td
import numpy as np
from pandas._testing import assert_frame_equal

exp_result = td.account_data([
    ['iban-1', '2021-01-01', 'Init money', np.NaN, np.NaN, np.NaN, 1000.00, 'PLN', np.NaN],
    ['iban-1', '2021-02-02', 'Out 1', np.NaN, np.NaN, np.NaN, -200.00, 'PLN', np.NaN],
    ['iban-1', '2021-03-03', 'Out 2', np.NaN, np.NaN, np.NaN, -3.33, 'PLN', np.NaN],
    ['iban-1', '2021-04-04', 'In 1', np.NaN, np.NaN, np.NaN, 3.33, 'PLN', np.NaN],
    ['iban-1', '2021-05-05', 'Out 3', np.NaN, np.NaN, np.NaN, -400.00, 'PLN', np.NaN],
    ['iban-1', '2021-06-06', 'In 2', np.NaN, np.NaN, np.NaN, 50.00, 'PLN', np.NaN]
])

test_data_path = str(pathlib.Path(__file__).parent.absolute()) + '/data/'

def test_load_pl_ing():
    # GIVEN
    ing_file = test_data_path + 'test_pl_ing.csv'

    # WHEN
    result = importer.load_bank_data(file_path=ing_file, contents=None, kind=models.Bank.PL_ING, account_id='iban-1')

    # THEN
    expected = __prepare_expected()
    result = __drop_empty_columns(result)
    assert_frame_equal(expected.reset_index(drop=True), result.reset_index(drop=True), check_names=False)

def test_load_pl_mbank():
    # GIVEN
    mbank_file = test_data_path + 'test_pl_mbank.csv'

    # WHEN
    result = importer.load_bank_data(file_path=mbank_file, contents=None, kind=models.Bank.PL_MBANK, account_id='iban-1')

    # THEN
    expected = __prepare_expected()
    result = __drop_empty_columns(result)
    assert_frame_equal(expected.reset_index(drop=True), result.reset_index(drop=True), check_names=False)

def test_load_pl_millenium():
    # GIVEN
    millenium_file = test_data_path + 'test_pl_millenium.csv'

    # WHEN
    result = importer.load_bank_data(file_path=millenium_file, contents=None, kind=models.Bank.PL_MILLENIUM, account_id='iban-1')

    # THEN
    expected = __prepare_expected()
    result = __drop_empty_columns(result)
    assert_frame_equal(expected.reset_index(drop=True), result.reset_index(drop=True))


def __prepare_expected():
    result = exp_result
    result['Account'] = result['Account'].astype('string')
    result = __drop_empty_columns(result)
    return result

def __drop_empty_columns(df):
    return df.drop(columns=['Details', 'Category', 'Comment', 'Balance'])
