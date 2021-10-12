import pytest

import scripts.main.ui as ui

def test_decode_bank_ids():
    # GIVEN
    bank_ids = ['PL_MBANK', 'GB_REVOLUT']

    # WHEN
    actual = ui.decode_bank_ids(bank_ids)

    # THEN
    assert [
        {'label': 'Poland - MBANK', 'value': 'PL_MBANK'},
        {'label': 'United Kingdom - REVOLUT', 'value': 'GB_REVOLUT'}
    ] == actual

def test_decode_mankkoo_id():
    # GIVEN
    bank_ids = ['MANKKOO']

    # WHEN
    actual = ui.decode_bank_ids(bank_ids)

    # THEN
    assert [
        {'label': 'MANKKOO', 'value': 'MANKKOO'}
    ] == actual
