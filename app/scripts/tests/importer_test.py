import pytest
import scripts.main.importer.importer as importer
import scripts.main.config as config
import scripts.main.models as models
import scripts.main.data as data
import numpy as np
import pandas as pd
from pandas._testing import assert_frame_equal

exp_result = pd.DataFrame(
    data=np.array([
    ['Bank', 'checking', 'Bank Account', '2021-01-01T00:00:00.000Z', 'Init money', np.NaN, np.NaN, np.NaN, 1000.00, 'PLN', np.NaN],
    ['Bank', 'checking', 'Bank Account', '2021-02-02T00:00:00.000Z', 'Out 1', np.NaN, np.NaN, np.NaN, -200.00, 'PLN', np.NaN],
    ['Bank', 'checking', 'Bank Account', '2021-03-03T00:00:00.000Z', 'Out 2', np.NaN, np.NaN, np.NaN, -3.33, 'PLN', np.NaN],
    ['Bank', 'checking', 'Bankm Account', '2021-04-04T00:00:00.000Z', 'In 1', np.NaN, np.NaN, np.NaN, 3.33, 'PLN', np.NaN],
    ['Bank', 'checking', 'Bank Account', '2021-05-05T00:00:00.000Z', 'Out 3', np.NaN, np.NaN, np.NaN, -400.00, 'PLN', np.NaN],
    ['Bank', 'checking', 'Bank Account', '2021-06-06T00:00:00.000Z', 'In 2', np.NaN, np.NaN, np.NaN, 50.00, 'PLN', np.NaN]
    ]),
    columns=data.account_columns
).astype({'Bank': 'string', 'Date': 'datetime64', 'Operation': 'float'})

def test_load_data(mocker):
    # GIVEN
    test_account = config.data_path() + config.account_file
    mocker.patch('scripts.main.config.mankoo_file_path', return_value=test_account)

    # WHEN
    result = importer.load_data(models.FileType.ACCOUNT)

    # THEN
    assert len(result) == 6

def test_load_pl_millenium():
    # GIVEN
    millenium_file = 'test_pl_millenium.csv'

    # WHEN
    result = importer.load_data(models.FileType.BANK, kind=models.Bank.PL_MILLENIUM, file_name=millenium_file)

    # THEN
    expected = __prepare_expected(exp_result, 'Millenium', 'Millenium Account')
    result = __drop_empty_columns(result)
    assert_frame_equal(expected.reset_index(drop=True), result.reset_index(drop=True))

def test_load_pl_ing():
    # GIVEN
    ing_file = 'test_pl_ing.csv'

    # WHEN
    result = importer.load_data(models.FileType.BANK, kind=models.Bank.PL_ING, file_name=ing_file)

    # THEN
    expected = __prepare_expected(exp_result, 'ING', 'ING Account')
    result = __drop_empty_columns(result)
    assert_frame_equal(expected.reset_index(drop=True), result.reset_index(drop=True))

def __prepare_expected(df, bank, account):
    result = __replace_placholders(df, bank, account)
    result = __drop_empty_columns(result)
    return result

def __replace_placholders(df, bank, account):
    df['Bank'] = bank
    df['Bank'] = df['Bank'].astype('string')
    df['Account'] = account
    df['Account'] = df['Account'].astype('string')
    return df

def __drop_empty_columns(df):
    return df.drop(columns=['Details', 'Category', 'Comment', 'Balance'])
