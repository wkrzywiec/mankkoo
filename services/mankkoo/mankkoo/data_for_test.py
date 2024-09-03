from datetime import datetime, timezone, timedelta

import uuid
import mankkoo.event_store as es


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
