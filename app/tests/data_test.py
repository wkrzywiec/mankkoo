import pytest
import app.scripts.data as data

def test_incorrect_bank():
    # GIVEN
    bank = 'NOT KNOWN BANK'

    # WHEN
    with pytest.raises(KeyError) as ex:
        data.add_new_operations(bank, 'not_known_bank.csv')

    # THEN
    assert 'Failed to load data from file. Not known bank. Was provided {} bank'.format(bank) in str(ex.value)

def test_add_new_operations():
    # GIVEN
    bank = data.Bank.PL_MILLENIUM

    # WHEN
    df = data.add_new_operations(bank, 'test_pl_millenium.csv')

    # THEN
    assert len(df) == 12