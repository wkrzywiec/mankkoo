import pytest
import app.scripts.importer as importer

def load_data_test():
    # GIVEN
    account_file = 'account.csv'

    # WHEN
    data = importer.load_data(account_file)

    # THEN
    assert len(data) != 0

def load_pl_millenium_test():
    # GIVEN
    millenium_file = 'test_pl_millenium.csv'

    # WHEN
    data = importer.load_pl_millenium(millenium_file)

    # THEN
    assert len(data) != 0
