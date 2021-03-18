import pytest
import app.scripts.importer as importer
from app.scripts.data import account_file 
import pandas as pd

def test_load_data():
    # WHEN
    data = importer.load_data(account_file)

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
