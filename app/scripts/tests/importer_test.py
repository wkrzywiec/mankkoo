import pytest
import scripts.main.importer.importer as importer
import scripts.main.config as config
import scripts.main.models as models
import pandas as pd

def test_load_data(mocker):
    # GIVEN
    test_account = config.data_path() + config.account_file
    mocker.patch('scripts.main.config.mankoo_file_path', return_value=test_account)

    # WHEN
    data = importer.load_data(models.FileType.ACCOUNT)

    # THEN
    assert len(data) == 6

def test_load_pl_millenium():
    # GIVEN
    millenium_file = 'test_pl_millenium.csv'

    # WHEN
    data = importer.load_data(models.FileType.BANK, kind=models.Bank.PL_MILLENIUM, file_name=millenium_file)

    # THEN
    assert len(data) == 6
    data['Bank'].dtypes == pd.StringDtype
    data['Date'].iloc[0] == '31/01/2021'
