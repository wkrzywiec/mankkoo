import pytest
import app.scripts.importer as importer
import app.scripts.config as config
import pandas as pd

def test_load_data(mocker):
    # GIVEN
    test_account = config.data_path() + config.account_file
    mocker.patch('app.scripts.config.mankoo_account_path', return_value=test_account)

    # WHEN
    data = importer.load_data(type='account')

    # THEN
    assert len(data) == 6

def test_load_pl_millenium():
    # GIVEN
    millenium_file = 'test_pl_millenium.csv'

    # WHEN
    data = importer.load_pl_millenium(millenium_file)

    # THEN
    assert len(data) == 6
    data['Bank'].dtypes == pd.StringDtype
    data['Date'].iloc[0] == '31/01/2021'
