import pytest
import app.scripts.importer as importer

def load_data_test():
    # GIVEN
    account_file = 'account.csv'

    # WHEN
    data = importer.load_data(account_file)

    # THEN
    assert len(data) != 0