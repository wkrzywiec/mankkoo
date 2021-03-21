import pytest
import app.scripts.data as data
import app.scripts.importer as importer
import numpy as np
import pandas as pd

start_data = pd.DataFrame(
    data=np.array([
    ['Millenium', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000, 'PLN', 1000],
    ['Millenium', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['Millenium', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.3, 'PLN', 774.48]
    ]),
    columns=data.columns
).astype({'Balance': 'float', 'Operation': 'float'})

millenium_data = pd.DataFrame(
    data=np.array([
        ['2021-03-15', 'Train ticket', 'PLN', -100, 'Millenium', np.NaN, np.NaN],
        ['2021-03-16', 'Bus ticket', 'PLN', -200, 'Millenium', np.NaN, np.NaN],
        ['2021-03-17', 'Salary', 'PLN', 3000.33, 'Millenium', np.NaN, np.NaN]
    ]),
    columns=["Date", "Title", "Currency", "Operation", "Bank", "Category", "Comment"]
    )

end_data = pd.DataFrame(
    data=np.array([
    ['Millenium', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000.00, 'PLN', 1000.00],
    ['Millenium', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['Millenium', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.30, 'PLN', 774.48],
    ['Millenium', '2021-03-15', 'Train ticket', np.NaN, np.NaN, np.NaN, -100.00, 'PLN', 674.48],
    ['Millenium', '2021-03-16', 'Bus ticket', np.NaN, np.NaN, np.NaN, -200.00, 'PLN', 474.48],
    ['Millenium', '2021-03-17', 'Salary', np.NaN, np.NaN, np.NaN, 3000.33, 'PLN', 3474.81]
    ]),
    columns=data.columns
).astype({'Balance': 'float', 'Operation': 'float'})

def test_incorrect_bank():
    # GIVEN
    bank = 'NOT KNOWN BANK'

    # WHEN
    with pytest.raises(KeyError) as ex:
        data.add_new_operations(bank, 'not_known_bank.csv')

    # THEN
    assert 'Failed to load data from file. Not known bank. Was provided {} bank'.format(bank) in str(ex.value)

def test_add_new_operations(mocker):
    # GIVEN
    bank = importer.Bank.PL_MILLENIUM

    mocker.patch('app.scripts.importer.load_pl_millenium', return_value=millenium_data)
    mocker.patch('app.scripts.importer.load_data', return_value=start_data)
    mocker.patch('pandas.DataFrame.to_csv')

    # WHEN
    df = data.add_new_operations(bank, 'test_pl_millenium.csv')

    # THEN
    assert df['Operation'].equals(end_data['Operation'])
    assert df['Balance'].equals(end_data['Balance'])
    assert df['Date'].equals(end_data['Date'])
