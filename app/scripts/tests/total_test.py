import pytest
import numpy as np
import pandas as pd
import scripts.main.data as data
import scripts.main.total as total

# TODO extract to separate class
start_data = pd.DataFrame(
    data=np.array([
    ['Millenium', 'checking', '360', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000, 'PLN', 1000],
    ['Millenium', 'checking', '360', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['Millenium', 'checking', '360', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.3, 'PLN', 774.48]
    ]),
    columns=data.account_columns
).astype({'Balance': 'float', 'Operation': 'float'})

millenium_data = pd.DataFrame(
    data=np.array([
        ['2021-03-15', 'Train ticket', 'PLN', -100, 'Millenium', np.NaN, np.NaN],
        ['2021-03-16', 'Bus ticket', 'PLN', -200, 'Millenium', np.NaN, np.NaN],
        ['2021-03-17', 'Salary', 'PLN', 3000.33, 'Millenium', np.NaN, np.NaN]
    ]),
    columns=['Date', 'Title', 'Currency', 'Operation', 'Bank', 'Category', 'Comment']
    )

end_data = pd.DataFrame(
    data=np.array([
    ['Millenium', 'checking', '360', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000.00, 'PLN', 1000.00],
    ['Millenium', 'checking', '360', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['Millenium', 'checking', '360', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.30, 'PLN', 774.48],
    ['Millenium', 'checking', '360', '2021-03-15', 'Train ticket', np.NaN, np.NaN, np.NaN, -100.00, 'PLN', 674.48],
    ['Millenium', 'checking', '360', '2021-03-16', 'Bus ticket', np.NaN, np.NaN, np.NaN, -200.00, 'PLN', 474.48],
    ['Millenium', 'checking', '360', '2021-03-17', 'Salary', np.NaN, np.NaN, np.NaN, 3000.33, 'PLN', 3474.81]
    ]),
    columns=data.account_columns
).astype({'Balance': 'float', 'Operation': 'float'})

investment = pd.DataFrame(
    data=np.array([
        [0, 'Bank Deposit', 'Bank A', 'Super Bank Deposit', '2016-11-28', '2017-04-09', 1000.00, 1079.89, 'PLN', np.NaN, np.NaN],
        [1, 'Bank Deposit', 'Bank B', 'Ultra Bank Deposit', '2020-01-01', np.NaN, 1000.00, np.NaN, 'PLN', np.NaN, np.NaN],
        [1, 'Bank Deposit', 'Bank A', 'Hiper Bank Deposit', '2020-11-28', np.NaN, 1000.00, np.NaN, 'PLN', np.NaN, np.NaN]
    ]),
    columns=data.invest_columns
).astype({'Active': 'int', 'Start Amount': 'float', 'End amount': 'float'})

stock = pd.DataFrame(
    data=np.array([
        ['Bank A', '2021-01-01', 'ETFSP500', 'Buy', 1000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN],
        ['Bank A', '2021-01-01', 'ETFDAX', 'Buy', 1000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN]
    ]),
    columns=data.stock_columns
).astype({'Total Value': 'float'})

def test_total_money_data():
    # GIVEN
    investment.Active = investment.Active.astype('bool')
    all_data = dict(
        account = start_data,
        investment = investment,
        stock = stock
    )

    # WHEN
    total_money = total.total_money_data(all_data)

    # THEN 
    assert total_money.to_dict('records') == [
        {'Type': 'Checking Account', 'Total': 774.48, 'Percentage': 0.16221242941639719},
        {'Type': 'Savings Account', 'Total': 0.00, 'Percentage': 0.0},
        {'Type': 'Cash', 'Total': 0.00, 'Percentage': 0.0},
        {'Type': 'PPK', 'Total': 0.00, 'Percentage': 0.0},
        {'Type': 'Investments', 'Total': 2000.00, 'Percentage': 0.41889378529180143},
        {'Type': 'Stocks', 'Total': 2000.00, 'Percentage': 0.41889378529180143}
    ]