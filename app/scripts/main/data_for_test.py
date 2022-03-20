import numpy as np
import pandas as pd
import scripts.main.data as data

start_data = [
    ['Millenium', 'checking', '360', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000, 'PLN', 1000],
    ['Millenium', 'checking', '360', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['Millenium', 'checking', '360', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.3, 'PLN', 774.48]
]

millenium_data = [
    ['Millenium', 'checking', '360', '2021-03-15', 'Train ticket', 'Detail new', np.NaN, np.NaN, -100, 'PLN', np.NaN],
    ['Millenium', 'checking', '360', '2021-03-16', 'Bus ticket', 'Detail new', np.NaN, np.NaN, -200, 'PLN', np.NaN],
    ['Millenium', 'checking', '360', '2021-03-17', 'Salary', 'Detail new', np.NaN, np.NaN, 3000.33, 'PLN', np.NaN]
]

end_data = [
    ['Millenium', 'checking', '360', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000.00, 'PLN', 1000.00],
    ['Millenium', 'checking', '360', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['Millenium', 'checking', '360', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.30, 'PLN', 774.48],
    ['Millenium', 'checking', '360', '2021-03-15', 'Train ticket', np.NaN, np.NaN, np.NaN, -100.00, 'PLN', 674.48],
    ['Millenium', 'checking', '360', '2021-03-16', 'Bus ticket', np.NaN, np.NaN, np.NaN, -200.00, 'PLN', 474.48],
    ['Millenium', 'checking', '360', '2021-03-17', 'Salary', np.NaN, np.NaN, np.NaN, 3000.33, 'PLN', 3474.81]
]

investment = [
    [0, 'Bank Deposit', 'Bank A', 'Super Bank Deposit', '2016-11-28', '2017-04-09', 1000.00, 1079.89, 'PLN', np.NaN, np.NaN],
    [1, 'Bank Deposit', 'Bank B', 'Ultra Bank Deposit', '2020-01-01', np.NaN, 1000.00, np.NaN, 'PLN', np.NaN, np.NaN],
    [1, 'Bank Deposit', 'Bank A', 'Hiper Bank Deposit', '2020-11-28', np.NaN, 1000.00, np.NaN, 'PLN', np.NaN, np.NaN]
]

stock = [
    ['Bank A', '2021-01-01', 'ETFSP500', 'Buy', 1000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN],
    ['Bank A', '2021-01-01', 'ETFDAX', 'Buy', 1000.00, 10, 'PLN', np.NaN, np.NaN, np.NaN]
]

total = [
    ['2021-01-01', 10],
    ['2021-01-01', 20]
]

def account_data(rows=start_data):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=data.account_columns
    ).astype({'Balance': 'float', 'Operation': 'float'})
    result['Date'] = pd.to_datetime(result['Date'], format='%Y-%m-%d', errors='coerce')
    result['Date'] = result['Date'].dt.date
    # result = result.set_index('Row')
    return result

def investment_data(rows=investment):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=data.invest_columns
    ).astype({'Active': 'int', 'Start Amount': 'float', 'End amount': 'float', 'Start Date': 'datetime64[ns]', 'End Date': 'datetime64[ns]'})
    result.Active = result.Active.astype('bool')
    result['Start Date'] = result['Start Date'].dt.date
    result['End Date'] = result['End Date'].dt.date
    return result

def stock_data(rows=stock):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=data.stock_columns
    ).astype({'Total Value': 'float', 'Date': 'datetime64[ns]'})
    result['Date'] = result['Date'].dt.date
    return result

def total_data(rows=total):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=data.total_columns
    ).astype({'Date': 'datetime64[ns]', 'Total': 'float'})
    result['Date'] = pd.to_datetime(result['Date'], format='%Y-%m-%d', errors='coerce')
    result['Date'] = result['Date'].dt.date
    return result
