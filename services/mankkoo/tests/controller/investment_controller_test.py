import uuid
from datetime import datetime

import mankkoo.event_store as es


def test_investment_wallets_endpoint__returns_wallet_list(test_client):
    # GIVEN
    wallets = ["Wallet A", "Wallet B", "Wallet C"]
    streams = []
    for wallet_label in wallets:
        stream = es.Stream(
            uuid.uuid4(),
            "investment",
            "deposit",
            "Super Investment",
            "Broker A",
            True,
            version=0,
            metadata={"details": "Super investment details"},
            labels={"wallet": wallet_label},
        )
        streams.append(stream)
    es.create(streams)

    # WHEN
    response = test_client.get("/api/investments/wallets")

    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    assert "wallets" in payload
    assert set(payload["wallets"]) == set(wallets)


def test_get_investments_no_query_params(test_client):
    # GIVEN
    streams = _create_investment_test_streams()
    # WHEN
    response = test_client.get("/api/investments")
    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    ids = [item["id"] for item in payload]
    # Should include all active and inactive investments, stocks, and savings
    # accounts
    for s in streams.values():
        assert str(s.id) in ids


def test_get_investments_inactive_only(test_client):
    # GIVEN
    streams = _create_investment_test_streams()
    # WHEN
    response = test_client.get("/api/investments?active=false")
    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    ids = [item["id"] for item in payload]
    # Only inactive investment and savings
    assert str(streams["investment_inactive"].id) in ids
    assert str(streams["savings_inactive"].id) in ids
    assert str(streams["investment"].id) not in ids
    assert str(streams["savings"].id) not in ids
    assert str(streams["etf"].id) not in ids


def test_get_investments_active_and_by_wallet(test_client):
    # GIVEN
    streams = _create_investment_test_streams()
    # WHEN
    response = test_client.get("/api/investments?active=true&wallet=Wallet%20B")
    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    ids = [item["id"] for item in payload]
    # Only active investment in Wallet B
    assert str(streams["investment"].id) in ids
    assert str(streams["investment_inactive"].id) not in ids
    assert str(streams["etf"].id) not in ids
    assert str(streams["savings"].id) not in ids
    assert str(streams["savings_inactive"].id) not in ids


def _create_investment_test_streams():
    # ETF stock (active)
    etf_stream = es.Stream(
        uuid.uuid4(),
        "stocks",
        "ETF",
        "SP500 ETF",
        "Broker1",
        True,
        0,
        {"details": "SP500 ETF details"},
        {"wallet": "Wallet A"},
    )
    # Investment (active)
    investment_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "deposit",
        "Bank Deposit",
        "Broker B",
        True,
        0,
        {"details": "Bank deposit details"},
        {"wallet": "Wallet B"},
    )
    # Investment (inactive)
    investment_stream_inactive = es.Stream(
        uuid.uuid4(),
        "investment",
        "deposit",
        "Old Investment",
        "Broker B",
        False,
        0,
        {"details": "Old investment details"},
        {"wallet": "Wallet B"},
    )
    # Savings account (active)
    savings_stream = es.Stream(
        uuid.uuid4(),
        "account",
        "savings",
        "My Savings Account",
        "Bank C",
        True,
        0,
        {"accountNumber": "1234567890"},
        {"wallet": "Wallet C"},
    )
    # Savings account (inactive)
    savings_stream_inactive = es.Stream(
        uuid.uuid4(),
        "account",
        "savings",
        "Old Savings Account",
        "Bank C",
        False,
        0,
        {"details": "Old savings account details"},
        {"wallet": "Wallet C"},
    )
    es.create(
        [
            etf_stream,
            investment_stream,
            investment_stream_inactive,
            savings_stream,
            savings_stream_inactive,
        ]
    )
    return {
        "etf": etf_stream,
        "investment": investment_stream,
        "investment_inactive": investment_stream_inactive,
        "savings": savings_stream,
        "savings_inactive": savings_stream_inactive,
    }


def test_get_investments_includes_gold(test_client):
    # GIVEN
    gold_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        "Physical Gold",
        "Gold Dealer",
        True,
        0,
        {"details": "Gold coins"},
        {"wallet": "Wallet A"},
    )
    bonds_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "treasury_bonds",
        "10-years Treasury Bonds",
        "Bank 1",
        True,
        0,
        {"details": "Some details"},
        {"wallet": "Wallet A"},
    )
    es.create([gold_stream, bonds_stream])

    gold_bought = es.Event(
        stream_type="investment",
        stream_id=gold_stream.id,
        event_type="GoldBought",
        data={
            "totalValue": 8500.0,
            "balance": 8500.0,
            "weight": 31.1,
            "totalWeight": 31.1,
            "unitPrice": 273.31,
            "currency": "PLN",
            "seller": "Mennica Polska",
            "goldSource": "1oz Krugerrand",
            "comment": "Purchase",
        },
        occured_at=datetime(2025, 1, 15),
        version=1,
    )
    bonds_bought = es.Event(
        stream_type="investment",
        stream_id=bonds_stream.id,
        event_type="TreasuryBondsBought",
        data={
            "totalValue": 1000.0,
            "balance": 1000.0,
            "units": 10,
            "pricePerUnit": 100.0,
            "currency": "PLN",
        },
        occured_at=datetime(2025, 1, 15),
        version=1,
    )
    es.store([gold_bought, bonds_bought])

    # WHEN
    response = test_client.get("/api/investments")

    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    ids = [item["id"] for item in payload]
    assert str(gold_stream.id) in ids
    assert str(bonds_stream.id) in ids

    # Verify gold stream data
    gold_items = [item for item in payload if item["id"] == str(gold_stream.id)]
    assert len(gold_items) == 1
    gold = gold_items[0]
    assert gold["name"] == "Physical Gold"
    assert gold["investmentType"] == "investment"
    assert gold["subtype"] == "gold"
    assert gold["balance"] == 8500.0


def test_get_gold_transactions(test_client):
    # GIVEN
    gold_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        "Physical Gold",
        "Gold Dealer",
        True,
        0,
        {"details": "Gold coins"},
        {"wallet": "Wallet A"},
    )
    es.create([gold_stream])

    gold_bought = es.Event(
        stream_type="investment",
        stream_id=gold_stream.id,
        event_type="GoldBought",
        data={
            "totalValue": 8500.0,
            "balance": 8500.0,
            "weight": 31.1,
            "totalWeight": 31.1,
            "unitPrice": 273.31,
            "currency": "PLN",
            "seller": "Mennica Polska",
            "goldSource": "1oz Krugerrand",
            "comment": "First purchase",
        },
        occured_at=datetime(2025, 1, 15),
        version=1,
    )
    gold_priced = es.Event(
        stream_type="investment",
        stream_id=gold_stream.id,
        event_type="GoldPriced",
        data={
            "totalValue": 0.0,
            "balance": 9330.0,
            "weight": 0.0,
            "totalWeight": 31.1,
            "unitPrice": 300.0,
            "currency": "PLN",
            "comment": "Monthly revaluation",
        },
        occured_at=datetime(2025, 2, 15),
        version=2,
    )
    gold_sold = es.Event(
        stream_type="investment",
        stream_id=gold_stream.id,
        event_type="GoldSold",
        data={
            "totalValue": 9330.0,
            "balance": 0.0,
            "weight": 31.1,
            "totalWeight": 0.0,
            "unitPrice": 300.0,
            "currency": "PLN",
            "buyer": "Mennica Polska",
            "goldSource": "1oz Krugerrand",
            "comment": "Sold all",
        },
        occured_at=datetime(2025, 3, 15),
        version=3,
    )
    es.store([gold_bought, gold_priced, gold_sold])

    # WHEN
    response = test_client.get(f"/api/investments/transactions/{gold_stream.id}")

    # THEN
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 3

    # Results are ordered by version DESC (sold, priced, bought)
    sold = payload[0]
    assert sold["eventType"] == "Gold Sold"
    assert sold["pricePerUnit"] == 300.0
    assert sold["unitsCount"] == 31.1
    assert sold["totalValue"] == 9330.0
    assert sold["balance"] == 0.0
    assert sold["comment"] == "Sold all"

    priced = payload[1]
    assert priced["eventType"] == "Gold Priced"
    assert priced["pricePerUnit"] == 300.0
    assert priced["unitsCount"] == 0.0
    assert priced["balance"] == 9330.0
    assert priced["comment"] == "Monthly revaluation"

    bought = payload[2]
    assert bought["eventType"] == "Gold Bought"
    assert bought["pricePerUnit"] == 273.31
    assert bought["unitsCount"] == 31.1
    assert bought["totalValue"] == 8500.0
    assert bought["balance"] == 8500.0
    assert bought["comment"] == "First purchase"
