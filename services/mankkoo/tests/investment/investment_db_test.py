import uuid
from datetime import datetime

import mankkoo.event_store as es
from mankkoo.investment import investment_db


def _create_gold_stream(
    active=True, wallet="Default", name="Physical Gold", bank="Gold Dealer"
):
    return es.Stream(
        uuid.uuid4(),
        "investment",
        "gold",
        name,
        bank,
        active,
        0,
        {"details": "Gold coins"},
        {"wallet": wallet},
    )


def _gold_bought_event(
    stream_id,
    total_value,
    balance,
    weight,
    total_weight,
    unit_price,
    version,
    date="2025-01-15",
):
    return es.Event(
        stream_type="investment",
        stream_id=stream_id,
        event_type="GoldBought",
        data={
            "totalValue": total_value,
            "balance": balance,
            "weight": weight,
            "totalWeight": total_weight,
            "unitPrice": unit_price,
            "currency": "PLN",
            "seller": "Mennica Polska",
            "goldSource": "1oz Krugerrand",
            "comment": "Purchase",
        },
        occured_at=datetime.strptime(date, "%Y-%m-%d"),
        version=version,
    )


def _gold_priced_event(
    stream_id, balance, total_weight, unit_price, version, date="2025-02-15"
):
    return es.Event(
        stream_type="investment",
        stream_id=stream_id,
        event_type="GoldPriced",
        data={
            "totalValue": 0.0,
            "balance": balance,
            "weight": 0.0,
            "totalWeight": total_weight,
            "unitPrice": unit_price,
            "currency": "PLN",
            "comment": "Monthly revaluation",
        },
        occured_at=datetime.strptime(date, "%Y-%m-%d"),
        version=version,
    )


def _gold_sold_event(
    stream_id,
    total_value,
    balance,
    weight,
    total_weight,
    unit_price,
    version,
    date="2025-03-15",
):
    return es.Event(
        stream_type="investment",
        stream_id=stream_id,
        event_type="GoldSold",
        data={
            "totalValue": total_value,
            "balance": balance,
            "weight": weight,
            "totalWeight": total_weight,
            "unitPrice": unit_price,
            "currency": "PLN",
            "buyer": "Mennica Polska",
            "goldSource": "1oz Krugerrand",
            "comment": "Sold all",
        },
        occured_at=datetime.strptime(date, "%Y-%m-%d"),
        version=version,
    )


def test_gold_stream_appears_in_investments():
    # GIVEN
    gold_stream = _create_gold_stream()
    es.create([gold_stream])

    gold_bought = _gold_bought_event(
        stream_id=gold_stream.id,
        total_value=8500.0,
        balance=8500.0,
        weight=31.1,
        total_weight=31.1,
        unit_price=273.31,
        version=1,
    )
    es.store([gold_bought])

    # WHEN
    result = investment_db.load_investments(active=None, wallet=None)

    # THEN
    assert len(result) == 1
    gold = result[0]
    assert gold["id"] == str(gold_stream.id)
    assert gold["name"] == "Physical Gold"
    assert gold["investmentType"] == "investment"
    assert gold["subtype"] == "gold"
    assert gold["balance"] == 8500.0


def test_gold_stream_with_gold_priced_shows_revalued_balance():
    # GIVEN
    gold_stream = _create_gold_stream()
    es.create([gold_stream])

    gold_bought = _gold_bought_event(
        stream_id=gold_stream.id,
        total_value=8500.0,
        balance=8500.0,
        weight=31.1,
        total_weight=31.1,
        unit_price=273.31,
        version=1,
    )
    # Revaluation: price went up to 300 PLN/g, balance = 31.1 * 300 = 9330.0
    gold_priced = _gold_priced_event(
        stream_id=gold_stream.id,
        balance=9330.0,
        total_weight=31.1,
        unit_price=300.0,
        version=2,
    )
    es.store([gold_bought, gold_priced])

    # WHEN
    result = investment_db.load_investments(active=None, wallet=None)

    # THEN
    assert len(result) == 1
    gold = result[0]
    assert gold["balance"] == 9330.0


def test_gold_stream_with_all_sold_shows_zero_balance():
    # GIVEN
    gold_stream = _create_gold_stream()
    es.create([gold_stream])

    gold_bought = _gold_bought_event(
        stream_id=gold_stream.id,
        total_value=8500.0,
        balance=8500.0,
        weight=31.1,
        total_weight=31.1,
        unit_price=273.31,
        version=1,
    )
    # Sell all gold: totalWeight becomes 0, balance becomes 0
    gold_sold = _gold_sold_event(
        stream_id=gold_stream.id,
        total_value=9330.0,
        balance=0.0,
        weight=31.1,
        total_weight=0.0,
        unit_price=300.0,
        version=2,
    )
    es.store([gold_bought, gold_sold])

    # WHEN
    result = investment_db.load_investments(active=None, wallet=None)

    # THEN
    assert len(result) == 1
    gold = result[0]
    assert gold["balance"] == 0.0


def test_gold_transactions_show_correct_fields():
    # GIVEN
    gold_stream = _create_gold_stream()
    es.create([gold_stream])

    gold_bought = _gold_bought_event(
        stream_id=gold_stream.id,
        total_value=8500.0,
        balance=8500.0,
        weight=31.1,
        total_weight=31.1,
        unit_price=273.31,
        version=1,
        date="2025-01-15",
    )
    gold_priced = _gold_priced_event(
        stream_id=gold_stream.id,
        balance=9330.0,
        total_weight=31.1,
        unit_price=300.0,
        version=2,
        date="2025-02-15",
    )
    gold_sold = _gold_sold_event(
        stream_id=gold_stream.id,
        total_value=9330.0,
        balance=0.0,
        weight=31.1,
        total_weight=0.0,
        unit_price=300.0,
        version=3,
        date="2025-03-15",
    )
    es.store([gold_bought, gold_priced, gold_sold])

    # WHEN
    transactions = investment_db.load_investment_transactions(str(gold_stream.id))

    # THEN — results are ordered by version DESC (sold, priced, bought)
    assert len(transactions) == 3

    # GoldSold (version 3, latest first)
    sold = transactions[0]
    assert sold["eventType"] == "Gold Sold"
    assert sold["pricePerUnit"] == 300.0
    assert sold["unitsCount"] == 31.1
    assert sold["totalValue"] == 9330.0
    assert sold["balance"] == 0.0

    # GoldPriced (version 2)
    priced = transactions[1]
    assert priced["eventType"] == "Gold Priced"
    assert priced["pricePerUnit"] == 300.0
    assert priced["unitsCount"] == 0.0
    assert priced["balance"] == 9330.0

    # GoldBought (version 1)
    bought = transactions[2]
    assert bought["eventType"] == "Gold Bought"
    assert bought["pricePerUnit"] == 273.31
    assert bought["unitsCount"] == 31.1
    assert bought["totalValue"] == 8500.0
    assert bought["balance"] == 8500.0


def test_inactive_gold_stream_excluded_when_active_filter():
    # GIVEN
    inactive_gold_stream = _create_gold_stream(active=False, name="Inactive Gold")
    es.create([inactive_gold_stream])

    gold_bought = _gold_bought_event(
        stream_id=inactive_gold_stream.id,
        total_value=5000.0,
        balance=5000.0,
        weight=20.0,
        total_weight=20.0,
        unit_price=250.0,
        version=1,
    )
    es.store([gold_bought])

    # WHEN
    result = investment_db.load_investments(active=True, wallet=None)

    # THEN
    assert len(result) == 0


def test_gold_stream_filtered_by_wallet():
    # GIVEN
    gold_wallet_a = _create_gold_stream(wallet="Wallet A", name="Gold A")
    gold_wallet_b = _create_gold_stream(wallet="Wallet B", name="Gold B")
    es.create([gold_wallet_a, gold_wallet_b])

    bought_a = _gold_bought_event(
        stream_id=gold_wallet_a.id,
        total_value=5000.0,
        balance=5000.0,
        weight=20.0,
        total_weight=20.0,
        unit_price=250.0,
        version=1,
    )
    bought_b = _gold_bought_event(
        stream_id=gold_wallet_b.id,
        total_value=10000.0,
        balance=10000.0,
        weight=40.0,
        total_weight=40.0,
        unit_price=250.0,
        version=1,
    )
    es.store([bought_a, bought_b])

    # WHEN
    result = investment_db.load_investments(active=None, wallet="Wallet A")

    # THEN
    assert len(result) == 1
    assert result[0]["id"] == str(gold_wallet_a.id)
    assert result[0]["name"] == "Gold A"
    assert result[0]["balance"] == 5000.0


def test_gold_coexists_with_other_investments():
    # GIVEN — create a gold stream and a treasury bonds stream
    gold_stream = _create_gold_stream(name="Physical Gold")
    bonds_stream = es.Stream(
        uuid.uuid4(),
        "investment",
        "treasury_bonds",
        "10-years Treasury Bonds",
        "Bank 1",
        True,
        0,
        {"details": "Some details about the investment"},
        {"wallet": "Default"},
    )
    es.create([gold_stream, bonds_stream])

    gold_bought = _gold_bought_event(
        stream_id=gold_stream.id,
        total_value=8500.0,
        balance=8500.0,
        weight=31.1,
        total_weight=31.1,
        unit_price=273.31,
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
    result = investment_db.load_investments(active=None, wallet=None)

    # THEN
    assert len(result) == 2
    ids = [item["id"] for item in result]
    assert str(gold_stream.id) in ids
    assert str(bonds_stream.id) in ids

    subtypes = [item["subtype"] for item in result]
    assert "gold" in subtypes
    assert "treasury_bonds" in subtypes
