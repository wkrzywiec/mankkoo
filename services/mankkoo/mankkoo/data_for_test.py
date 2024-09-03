from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
import uuid
import mankkoo.database as db
import mankkoo.event_store as es

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


def any_account_stream(account_type="checking"):
    return any_stream(account_type=account_type)


def any_stream(stream_type='account', account_type="checking"):
    return es.Stream(uuid.uuid4(), stream_type, 0, {
        "active": True, "alias": "Bank account A", "bankName": "Bank A",
        "bankUrl": "https://www.bank-a.com", "accountNumber": "iban-1",
        "accountName": "Super Personal account", "accountType": account_type, "importer": "PL_MILLENIUM"
    })


def an_account_with_operations(operations: list[dict], type="checking") -> dict:
    account_stream = any_account_stream(account_type=type)
    first_operation_date = datetime.strptime(operations[0]['date'], '%d-%m-%Y')
    events = [account_opened_event(account_stream.id, occured_at=first_operation_date - timedelta(days=1))]
    balance = 0
    version = 1
    for operation in operations:
        version += 1
        event = account_operation_event(account_stream.id, operation['operation'], balance, version, datetime.strptime(operation['date'], '%d-%m-%Y'))
        events.append(event)
        balance = event.data['balance']

    return {"stream": account_stream, "events": events}


def account_opened_event(stream_id: uuid.UUID, occured_at=datetime.now(timezone.utc) - timedelta(days=1), stream_type='account') -> es.Event:
    return es.Event(
        stream_type=stream_type,
        stream_id=stream_id,
        event_type='AccountOpened',
        data={
            "balance": 0.00,
            "number": "PL1234567890",
            "isActive": True,
            "openedAt": occured_at.strftime("%d-%m-%Y %H:%M:%S")
        },
        occured_at=occured_at)


def account_operation_event(stream_id: uuid.UUID, operation: float, balance: float, version: int, occured_at: datetime, stream_type='account') -> es.Event:
    return es.Event(
        stream_type=stream_type,
        stream_id=stream_id,
        event_type='MoneyDeposited' if operation >= 0 else 'MoneyWithdrawn',
        data={
            "amount": operation,
            "balance": balance + operation,
            "title": "Some transacation",
            "currency": "PLN"
        },
        occured_at=occured_at,
        version=version)


def stock_events(operations: list[dict]) -> dict:
    events = []
    balance = 0
    version = 0
    stock_stream = es.Stream(uuid.uuid4(), 'stocks', 0, {"type": "ETF", "broker": "Bank 1"})

    for operation in operations:
        balance += operation['operation']
        version += 1
        event = es.Event(
            stream_type='stocks',
            stream_id=stock_stream.id,
            event_type='ETFBought' if operation['operation'] >= 0 else 'ETFSold',
            data={
                "totalValue": operation['operation'],
                "balance": balance,
                "units": 2,
                "averagePrice": (operation['operation'] / 2),
                "currency": "PLN"
            },
            occured_at=datetime.strptime(operation['date'], '%d-%m-%Y'),
            version=version
        )
        events.append(event)

    return {"stream": stock_stream, "events": events}


def investment_events(operations: list[dict]) -> dict:
    events = []
    balance = 0
    version = 0
    inv_stream = es.Stream(uuid.uuid4(), 'investment', 0, {"investmentName": "10-years Treasury Bonds", "category": "treasury_bonds", "active": True})

    for operation in operations:
        balance += operation['operation']
        version += 1
        event = es.Event(
            stream_type='investment',
            stream_id=inv_stream.id,
            event_type='TreasuryBondsBought' if operation['operation'] >= 0 else 'TreasuryBondsMatured',
            data={
                "totalValue": operation['operation'],
                "balance": balance,
                "units": 2,
                "pricePerUnit": (operation['operation'] / 2),
                "currency": "PLN"
            },
            occured_at=datetime.strptime(operation['date'], '%d-%m-%Y'),
            version=version
        )
        events.append(event)
    return {"stream": inv_stream, "events": events}


def retirment_events(operations: list[dict]) -> dict:
    account_stream = any_stream(stream_type='retirement')
    first_operation_date = datetime.strptime(operations[0]['date'], '%d-%m-%Y')
    events = [account_opened_event(account_stream.id, occured_at=first_operation_date - timedelta(days=1))]
    balance = 0
    version = 1
    for operation in operations:
        version += 1
        event = account_operation_event(account_stream.id, operation['operation'], balance, version, datetime.strptime(operation['date'], '%d-%m-%Y'), stream_type=account_stream.type)
        balance = event.data['balance']
        events.append(event)

    return {"stream": account_stream, "events": events}


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
