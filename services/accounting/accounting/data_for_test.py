from datetime import datetime
import numpy as np
import pandas as pd
import accounting.database as db

user_config = {
    'accounts': {
        'definitions': [
            {
                'active': True,
                'alias': 'Bank account A',
                'bank': 'Bank A',
                'bank_url': 'https://www.bank-a.com',
                'id': 'iban-1',
                'name': 'Super Personal account',
                'type': 'checking',
                'importer': 'PL_MILLENIUM'
            },
            {
                'active': True,
                'alias': 'Saving account',
                'bank': 'Bank A',
                'bank_url': 'https://www.bank-a.com',
                'id': 'iban-11',
                'name': 'Super Savings account',
                'type': 'savigs',
                'importer': 'PL_MILLENIUM'
            },
            {
                'active': True,
                'alias': 'Bank account B',
                'bank': 'Bank B',
                'bank_url': 'https://www.bank-b.com',
                'id': 'iban-2',
                'name': 'Super Personal account',
                'type': 'checking',
                'importer': 'PL_MILLENIUM'
            },
            {
                'active': True,
                'alias': 'Bank account C',
                'bank': 'Bank C',
                'bank_url': 'https://www.bank-c.com',
                'id': 'iban-3',
                'name': 'Super Personal account',
                'type': 'checking',
                'importer': 'PL_MBANK'
            },
            {
                'active': True,
                'alias': 'Bank account D',
                'bank': 'Bank D',
                'bank_url': 'https://www.bank-d.com',
                'id': 'iban-4',
                'name': 'Super Personal account',
                'type': 'checking',
                'importer': 'PL_ING'
            },
            {
                'active': True,
                'alias': 'Wallet',
                'bank': 'My Socks',
                'bank_url': '',
                'id': 'cash',
                'name': 'Cash',
                'type': 'checking',
                'importer': 'MANKKOO'
            },
            {
                'active': True,
                'alias': 'PPK',
                'bank': 'PPK',
                'bank_url': 'https://www.ppk.com',
                'id': 'pko-ppk',
                'name': 'PPK account',
                'type': 'retirement',
                'importer': 'MANKKOO'
            }
        ]
    }
}

start_data = [
    ['iban-1', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000, 'PLN', 1000],
    ['iban-1', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['iban-1', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.3, 'PLN', 774.48]
]

millenium_data = [
    ['iban-1', '2021-03-15', 'Train ticket', 'Detail new', np.NaN, np.NaN, -100, 'PLN', np.NaN],
    ['iban-1', '2021-03-16', 'Bus ticket', 'Detail new', np.NaN, np.NaN, -200, 'PLN', np.NaN],
    ['iban-1', '2021-03-17', 'Salary', 'Detail new', np.NaN, np.NaN, 3000.33, 'PLN', np.NaN]
]

end_data = [
    ['iban-1', '2021-01-31', 'Init money', 'Detail 1', np.NaN, 'init', 1000.00, 'PLN', 1000.00],
    ['iban-1', '2021-01-31', 'Armchair', 'Detail 2', np.NaN, np.NaN, -222.22, 'PLN', 777.78],
    ['iban-1', '2021-01-31', 'Candies', 'Detail 3', np.NaN, np.NaN, -3.30, 'PLN', 774.48],
    ['iban-1', '2021-03-15', 'Train ticket', np.NaN, np.NaN, np.NaN, -100.00, 'PLN', 674.48],
    ['iban-1', '2021-03-16', 'Bus ticket', np.NaN, np.NaN, np.NaN, -200.00, 'PLN', 474.48],
    ['iban-1', '2021-03-17', 'Salary', np.NaN, np.NaN, np.NaN, 3000.33, 'PLN', 3474.81]
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
        columns=db.account_columns
    ).astype({'Balance': 'float', 'Operation': 'float'})
    result['Date'] = pd.to_datetime(result['Date'], format='%Y-%m-%d', errors='coerce')
    result['Date'] = result['Date'].dt.date
    return result

def investment_data(rows=investment):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=db.invest_columns
    ).astype({'Active': 'int', 'Start Amount': 'float', 'End amount': 'float', 'Start Date': 'datetime64[ns]', 'End Date': 'datetime64[ns]'})
    result.Active = result.Active.astype('bool')
    result['Start Date'] = result['Start Date'].dt.date
    result['End Date'] = result['End Date'].dt.date
    return result

def stock_data(rows=stock):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=db.stock_columns
    ).astype({'Total Value': 'float', 'Date': 'datetime64[ns]'})
    result['Date'] = result['Date'].dt.date
    return result

def total_data(rows=total):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=db.total_columns
    ).astype({'Date': 'datetime64[ns]', 'Total': 'float'})
    result['Date'] = pd.to_datetime(result['Date'], format='%Y-%m-%d', errors='coerce')
    result['Date'] = result['Date'].dt.date
    return result

def total_monthly_data(rows=total):
    result = pd.DataFrame(
        data=np.array(rows),
        columns=db.total_monthly_columns
    ).astype({'Date': 'datetime64[ns]', 'Income': 'float', 'Spending': 'float', 'Profit': 'float'})
    result['Date'] = pd.to_datetime(result['Date'], format='%Y-%m-%d', errors='coerce')
    result['Date'] = result['Date'].dt.date
    return result
