import uuid
from datetime import datetime, timedelta, timezone

import mankkoo.event_store as es


def any_account_stream(
    account_type: str = "checking",
    active: bool = True,
    wallet: str = "Default",
    include_in_wealth: bool | None = None,
) -> es.Stream:
    return any_stream(
        stream_subtype=account_type,
        active=active,
        wallet=wallet,
        include_in_wealth=include_in_wealth,
    )


def any_stream(
    stream_type: str = "account",
    stream_subtype: str = "checking",
    stream_name: str = f"Stream Name {str(uuid.uuid4())}",
    bank: str = f"Bank {str(uuid.uuid4())}",
    active: bool = True,
    wallet: str = "Default",
    include_in_wealth: bool | None = None,
) -> es.Stream:
    labels = {"wallet": wallet}
    if include_in_wealth is not None:
        labels["include_in_wealth"] = "true" if include_in_wealth else "false"

    return es.Stream(
        uuid.uuid4(),
        stream_type,
        stream_subtype,
        stream_name,
        bank,
        active,
        0,
        {
            "alias": "Bank account A",
            "bankName": "Bank A",
            "bankUrl": "https://www.bank-a.com",
            "accountNumber": "iban-1",
            "importer": "PL_MILLENIUM",
        },
        labels,
    )


def an_account_with_operations(
    operations: list[dict],
    type: str = "checking",
    active: bool = True,
    wallet: str = "Default",
    include_in_wealth: bool | None = None,
) -> dict:
    account_stream = any_account_stream(
        account_type=type,
        active=active,
        wallet=wallet,
        include_in_wealth=include_in_wealth,
    )
    first_operation_date = datetime.strptime(operations[0]["date"], "%d-%m-%Y")
    events = [
        account_opened_event(
            account_stream.id, occured_at=first_operation_date - timedelta(days=1)
        )
    ]
    balance = 0
    version = 1
    for operation in operations:
        version += 1
        event = account_operation_event(
            account_stream.id,
            operation["operation"],
            balance,
            version,
            datetime.strptime(operation["date"], "%d-%m-%Y"),
        )
        events.append(event)
        balance = event.data["balance"]

    return {"stream": account_stream, "events": events}


def account_opened_event(
    stream_id: uuid.UUID,
    occured_at=datetime.now(timezone.utc) - timedelta(days=1),
    stream_type="account",
) -> es.Event:
    return es.Event(
        stream_type=stream_type,
        stream_id=stream_id,
        event_type="AccountOpened",
        data={
            "balance": 0.00,
            "number": "PL1234567890",
            "isActive": True,
            "openedAt": occured_at.strftime("%d-%m-%Y %H:%M:%S"),
        },
        occured_at=occured_at,
    )


def account_operation_event(
    stream_id: uuid.UUID,
    operation: float,
    balance: float,
    version: int,
    occured_at: datetime,
    stream_type="account",
) -> es.Event:
    return es.Event(
        stream_type=stream_type,
        stream_id=stream_id,
        event_type="MoneyDeposited" if operation >= 0 else "MoneyWithdrawn",
        data={
            "amount": operation,
            "balance": balance + operation,
            "title": "Some transacation",
            "currency": "PLN",
        },
        occured_at=occured_at,
        version=version,
    )


def stock_events(
    operations: list[dict],
    type: str = "ETF",
    active: bool = True,
    wallet: str = "Default",
    include_in_wealth: bool | None = None,
) -> dict:
    events = []
    balance = 0
    version = 0
    labels = {"wallet": wallet}
    if include_in_wealth is not None:
        labels["include_in_wealth"] = "true" if include_in_wealth else "false"

    stock_stream = es.Stream(
        uuid.uuid4(),
        "stocks",
        type,
        "Stock Stream Name",
        "Bank 1",
        active,
        0,
        {"details": "Some details about the stock"},
        labels,
    )

    for operation in operations:
        balance += operation["operation"]
        version += 1
        event = es.Event(
            stream_type="stocks",
            stream_id=stock_stream.id,
            event_type="ETFBought" if operation["operation"] >= 0 else "ETFSold",
            data={
                "totalValue": operation["operation"],
                "balance": balance,
                "units": 2,
                "averagePrice": (operation["operation"] / 2),
                "currency": "PLN",
            },
            occured_at=datetime.strptime(operation["date"], "%d-%m-%Y"),
            version=version,
        )
        events.append(event)

    return {"stream": stock_stream, "events": events}


def investment_events(
    operations: list[dict],
    category: str = "treasury_bonds",
    active: bool = True,
    wallet: str = "Default",
    include_in_wealth: bool | None = None,
) -> dict:
    events = []
    balance = 0
    version = 0
    labels = {"wallet": wallet}
    if include_in_wealth is not None:
        labels["include_in_wealth"] = "true" if include_in_wealth else "false"

    inv_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        category,
        "10-years Treasury Bonds",
        "Bank 1",
        active,
        0,
        {"details": "Some details about the investment"},
        labels,
    )

    for operation in operations:
        balance += operation["operation"]
        version += 1
        event = es.Event(
            stream_type="investment",
            stream_id=inv_stream.id,
            event_type=(
                "TreasuryBondsBought"
                if operation["operation"] >= 0
                else "TreasuryBondsMatured"
            ),
            data={
                "totalValue": operation["operation"],
                "balance": balance,
                "units": 2,
                "pricePerUnit": (operation["operation"] / 2),
                "currency": "PLN",
            },
            occured_at=datetime.strptime(operation["date"], "%d-%m-%Y"),
            version=version,
        )
        events.append(event)
    return {"stream": inv_stream, "events": events}


def gold_events(
    operations: list[dict],
    active: bool = True,
    wallet: str = "Default",
    include_in_wealth: bool | None = None,
) -> dict:
    events = []
    balance = 0
    total_weight = 0
    version = 0
    labels = {"wallet": wallet}
    if include_in_wealth is not None:
        labels["include_in_wealth"] = "true" if include_in_wealth else "false"

    gold_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        "Physical Gold",
        "Gold Dealer",
        active,
        0,
        {"details": "Gold coins"},
        labels,
    )

    for operation in operations:
        version += 1
        event_type = operation.get("event_type", "GoldBought")
        weight = operation.get("weight", 0)
        unit_price = operation.get("unitPrice", 0)
        total_value = operation.get("totalValue", 0)
        comment = operation.get("comment", "")

        if event_type == "GoldBought":
            balance += total_value
            total_weight += weight
            data = {
                "totalValue": total_value,
                "balance": balance,
                "weight": weight,
                "totalWeight": total_weight,
                "unitPrice": unit_price,
                "currency": "PLN",
                "seller": operation.get("seller", ""),
                "goldSource": operation.get("goldSource", ""),
                "comment": comment,
            }
        elif event_type == "GoldSold":
            total_weight -= weight
            balance = total_weight * unit_price
            data = {
                "totalValue": total_value,
                "balance": balance,
                "weight": weight,
                "totalWeight": total_weight,
                "unitPrice": unit_price,
                "currency": "PLN",
                "buyer": operation.get("buyer", ""),
                "goldSource": operation.get("goldSource", ""),
                "comment": comment,
            }
        elif event_type == "GoldPriced":
            balance = total_weight * unit_price
            data = {
                "totalValue": 0.0,
                "balance": balance,
                "weight": 0.0,
                "totalWeight": total_weight,
                "unitPrice": unit_price,
                "currency": "PLN",
                "comment": comment,
            }
        else:
            raise ValueError(f"Unknown gold event type: {event_type}")

        event = es.Event(
            stream_type="investment",
            stream_id=gold_stream.id,
            event_type=event_type,
            data=data,
            occured_at=datetime.strptime(operation["date"], "%d-%m-%Y"),
            version=version,
        )
        events.append(event)

    return {"stream": gold_stream, "events": events}


def retirement_events(
    operations: list[dict], include_in_wealth: bool | None = None
) -> dict:
    account_stream = any_stream(
        stream_type="retirement", include_in_wealth=include_in_wealth
    )
    first_operation_date = datetime.strptime(operations[0]["date"], "%d-%m-%Y")
    events = [
        account_opened_event(
            account_stream.id, occured_at=first_operation_date - timedelta(days=1)
        )
    ]
    balance = 0
    version = 1
    for operation in operations:
        version += 1
        event = account_operation_event(
            account_stream.id,
            operation["operation"],
            balance,
            version,
            datetime.strptime(operation["date"], "%d-%m-%Y"),
            stream_type=account_stream.type,
        )
        balance = event.data["balance"]
        events.append(event)

    return {"stream": account_stream, "events": events}
