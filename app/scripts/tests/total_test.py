import pytest
import numpy as np
from pandas._testing import assert_frame_equal
import datetime
from dateutil.relativedelta import relativedelta
import scripts.main.total as total
import scripts.main.data_for_test as td
import scripts.main.database as real_data
import scripts.main.data_formatter as formatter

# not actual test, used only to debug real data, uncomment to use
# def test_real_total_money_data():
#     # GIVEN
#     all_data = real_data.load_data()

#     # WHEN
#     total_money = total.total_money_data(all_data)

#     # THEN
#     assert True

def test_total_money_data():
    # GIVEN
    all_data = dict(
        account=td.account_data(td.start_data),
        investment=td.investment_data(),
        stock=td.stock_data()
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

def test_total_money_data_for_checking_accounts():
    # GIVEN
    all_data = dict(
        account=td.account_data([
            ['Millenium', 'checking', '360', '2021-01-01', 'Init money', 'Detail 1', np.NaN, 'init', 1000, 'PLN', 2000],
            ['Millenium', 'checking', '360', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', -1000, 'PLN', 1000],
            ['Bank B', 'checking', 'Account name', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 1000]
        ]),
        investment=td.investment_data(),
        stock=td.stock_data()
    )

    # WHEN
    total_money = total.total_money_data(all_data)

    # THEN
    assert total_money[total_money['Type'] == 'Checking Account'].iloc[0]['Total'] == 2000.0

def test_accounts_balance_for_day_multiple_accounts():
    # GIVEN
    account = td.account_data([
        ['Millenium', 'checking', '360', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000, 'PLN', 1000],
        ['ING', 'checking', 'Direct', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 1000],
        ['mBank', 'checking', 'eKonto', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.3, 'PLN', 1000],
        ['Skarpeta', 'cash', 'Gotówka', '2021-01-31', 'a', 'a', np.NaN, np.NaN, 1000, 'PLN', 1000],
        ['Millenium', 'savings', 'Konto Oszczędnościowe Profit', '2021-01-31', 'a', 'a', np.NaN, np.NaN, 1000, 'PLN', 1000],
        ['PKO', 'retirement', 'PKO PPK', '2021-01-31', 'a', 'a', np.NaN, np.NaN, 1000, 'PLN', 1000],
        ['mBank', 'checking', 'eKonto', '2035-08-08', 'a', 'a', np.NaN, np.NaN, 10000, 'PLN', 10000]
    ])

    # WHEN
    total_balance = total.accounts_balance_for_day(account, datetime.date(2021, 1, 31))

    # THEN
    assert total_balance == 6000

def test_accounts_balance_for_day_multiple_accounts_in_different_days():
    # GIVEN
    account = td.account_data([
        ['Millenium', 'checking', '360', '2021-01-01', 'a', 'a', np.NaN, '', 1000, 'PLN', 1000],
        ['ING', 'checking', 'Direct', '2021-01-31', 'a', 'a', np.NaN, np.NaN, -222.22, 'PLN', 1000],
        ['mBank', 'checking', 'eKonto', '2021-02-01', 'a', 'a', np.NaN, np.NaN, -3.3, 'PLN', 2000],
        ['mBank', 'checking', 'eKonto', '2021-02-01', 'a', 'a', np.NaN, np.NaN, 1000, 'PLN', 3000],
        ['mBank', 'checking', 'eKonto', '2035-08-08', 'a', 'a', np.NaN, np.NaN, 10000, 'PLN', 10000]
    ])

    # WHEN
    total_balance = total.accounts_balance_for_day(account, datetime.date(2021, 2, 1))

    # THEN
    assert total_balance == 5000

def test_investments_for_day():
    # GIVEN
    investment = td.investment_data([
        [0, 'Bank Deposit', 'Bank A', 'Super Bank Deposit', '2016-11-28', '2017-04-09', 1000.00, 1079.89, 'PLN', np.NaN, np.NaN],
        [1, 'Bank Deposit', 'Bank B', 'Ultra Bank Deposit', '2020-01-01', '2021-01-01', 1000.00, np.NaN, 'PLN', np.NaN, np.NaN],
        [1, 'Bank Deposit', 'Bank A', 'Hiper Bank Deposit', '2020-11-28', '2021-11-28', 1000.00, np.NaN, 'PLN', np.NaN, np.NaN],
        [1, 'Bank Deposit', 'Bank A', 'Hiper Bank Deposit', '2020-11-28', np.NaN, 1000.00, np.NaN, 'PLN', np.NaN, np.NaN],
        [1, 'Bank Deposit', 'Bank A', 'Hiper Bank Deposit', '2035-08-08', np.NaN, 10000.00, np.NaN, 'PLN', np.NaN, np.NaN]
    ])

    # WHEN
    total_inv = total.investments_for_day(investment, datetime.date(2021, 1, 1))

    # THEN
    assert total_inv == 3000

def test_stock_for_day():
    # GIVEN
    stock = td.stock_data([
        ['Bank A', '2021-01-01', 'ETFSP500', 'Buy', 1000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN],
        ['Bank A', '2021-01-01', 'ETFDAX', 'Buy', 1000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN],
        ['Bank A', '2021-01-02', 'ETFDAX', 'Sell', 100.00, 1, 'PLN', np.NaN, np.NaN, np.NaN],
        ['Bank A', '2032-11-27', 'ETFSP500', 'Buy', 10000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN]
    ])

    # WHEN
    total_stock = total.stock_for_day(stock, datetime.date(2021, 1, 2))

    # THEN
    assert total_stock == 1900

def test_update_total_money(mocker):
    # GIVEN
    account = td.account_data([
        ['Millenium', 'checking', '360', '2021-01-01', 'a', 'a', np.NaN, '', 1000, 'PLN', 1000],
        ['ING', 'checking', 'Direct', '2021-01-01', 'a', 'a', np.NaN, np.NaN, -222.22, 'PLN', 1000],
        ['mBank', 'checking', 'eKonto', '2021-01-03', 'a', 'a', np.NaN, np.NaN, -3.3, 'PLN', 2000],
        ['mBank', 'checking', 'eKonto', '2021-01-03', 'a', 'a', np.NaN, np.NaN, 1000, 'PLN', 3000],
        ['ING', 'checking', 'Direct', '2021-01-04', 'a', 'a', np.NaN, np.NaN, -222.22, 'PLN', 2000],
        ['mBank', 'checking', 'eKonto', '2021-01-05', 'a', 'a', np.NaN, np.NaN, 10000, 'PLN', 10000]
    ])
    updated_dates = account.tail(3)['Date']

    # set other data
    old_total = td.total_data([
        ['2021-01-01', 10],
        ['2021-01-01', 20]
    ])
    inv_data = td.investment_data([
        [0, 'Bank Deposit', 'Bank A', 'Super Bank Deposit', '2016-11-28', '2017-04-09', 1000.00, 1079.89, 'PLN', np.NaN, np.NaN],
        [1, 'Bank Deposit', 'Bank B', 'Ultra Bank Deposit', '2020-01-01', np.NaN, 1000.00, np.NaN, 'PLN', np.NaN, np.NaN],
        [1, 'Bank Deposit', 'Bank A', 'Hiper Bank Deposit', '2020-11-28', np.NaN, 1000.00, np.NaN, 'PLN', np.NaN, np.NaN]
    ])
    stocks = td.stock_data([
        ['Bank A', '2021-01-01', 'ETFSP500', 'Buy', 1000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN],
        ['Bank A', '2021-01-01', 'ETFDAX', 'Buy', 1000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN]
    ])
    mocker.patch('scripts.main.database.load_total', side_effect=[old_total])
    mocker.patch('scripts.main.database.load_investments', side_effect=[inv_data])
    mocker.patch('scripts.main.database.load_stocks', side_effect=[stocks])
    mocker.patch('pandas.DataFrame.to_csv')

    from_date = formatter.map_date('2021-01-01')
    till_date = formatter.map_date('2021-01-05')

    # WHEN
    result = total.update_total_money(account, from_date, till_date)

    # THEN
    expected = td.total_data([
        ['2021-01-01', 6000],
        ['2021-01-02', 6000],
        ['2021-01-03', 9000],
        ['2021-01-04', 10000],
        ['2021-01-05', 17000],
    ])
    assert_frame_equal(expected, result)

def test_update_monthly_profit(mocker):
    # GIVEN
    old_total_monthly = td.total_monthly_data([
        ['2021-01-01', 0, 0, 100],
        ['2021-02-01', 0, 0, 200]
    ])

    mocker.patch('scripts.main.database.load_total_monthly', side_effect=[old_total_monthly])
    
    
    total_data = td.total_data([
        ['2021-01-01', 100],
        ['2021-02-01', 200],
        ['2021-03-01', 300],
        ['2021-04-01', 400],
        ['2021-05-01', 500],
        ['2021-06-01', 600]
    ])

    mocker.patch('scripts.main.database.load_total', side_effect=[total_data])
    mocker.patch('pandas.DataFrame.to_csv')

    # WHEN
    result = total.update_monthly_profit(from_date=datetime.date(2021, 3, 10), till_date=datetime.date(2021, 6, 12))

    # THEN
    expected = td.total_monthly_data([
        ['2021-01-01', 0, 0, 100],
        ['2021-02-01', 0, 0, 200],
        ['2021-03-01', 0, 0, 100],
        ['2021-04-01', 0, 0, 100],
        ['2021-05-01', 0, 0, 100],
        ['2021-06-01', 0, 0, 100]
    ])
    assert_frame_equal(expected, result)



def test_last_month_income():
    # GIVEN
    total_data = td.total_data([
        ['2020-12-25', 5],
        ['2021-01-01', 10],
        ['2021-01-15', 20],
        ['2021-02-08', 30],
        ['2021-02-28', 40],
        ['2021-03-03', 50],
    ])

    # WHEN
    result = total.last_month_income(total_data, datetime.date(2021, 3, 3))

    # THEN
    assert result == 20
