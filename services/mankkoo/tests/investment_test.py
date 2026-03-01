from datetime import datetime
import uuid

import pytest

import mankkoo.event_store as es
from mankkoo.investment import investment


def test_map_event_type_happy_path():
    assert investment.__map_event_type("ETF", "buy") == "ETFBought"
    assert (
        investment.__map_event_type("treasury_bonds", "price_update")
        == "TreasuryBondsPriced"
    )


def test_map_event_type_invalid_raises_value_error():
    with pytest.raises(ValueError):
        investment.__map_event_type("ETF", "bonus")


def test_calculate_unit_price_returns_ratio():
    assert investment.__calculate_unit_price(1000.0, 10.0) == 100.0


def test_calculate_unit_price_rejects_zero_units():
    with pytest.raises(ValueError):
        investment.__calculate_unit_price(1000.0, 0.0)


def test_validate_buy_event_data_allows_positive_values():
    investment.__validate_buy_event_data(units=10.0, total_value=500.0)


def test_validate_buy_event_data_rejects_zero_units():
    with pytest.raises(ValueError, match="Units must be greater than zero"):
        investment.__validate_buy_event_data(units=0.0, total_value=500.0)


def test_validate_sell_event_data_allows_positive_values():
    investment.__validate_sell_event_data(units=5.0, total_value=250.0)


def test_validate_sell_event_data_rejects_zero_total_value():
    with pytest.raises(ValueError, match="Total value must be greater than zero"):
        investment.__validate_sell_event_data(units=5.0, total_value=0.0)


def test_validate_price_update_data_requires_units():
    with pytest.raises(ValueError, match="Cannot update price without owned units"):
        investment.__validate_price_update_data(total_value=100.0, current_units=0.0)


def test_validate_price_update_data_allows_positive_flow():
    investment.__validate_price_update_data(total_value=1250.0, current_units=10.0)


def test_create_etf_bought_event_updates_balance():
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    payload, status = investment.create_investment_event_entry(
        {
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-15",
            "units": 10.0,
            "totalValue": 1000.0,
            "comment": "initial",
        }
    )

    assert status == 201
    assert payload["result"] == "Success"
    events = es.load(stream.id)
    assert events[0].event_type == "ETFBought"
    assert events[0].data["balance"] == 1000.0
    assert events[0].data["averagePrice"] == 100.0
    assert events[0].data["comment"] == "initial"


def test_create_etf_sold_event_stores_negative_units():
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    es.store(
        [
            es.Event(
                stream_type="stocks",
                stream_id=stream.id,
                event_type="ETFBought",
                data={
                    "totalValue": 1200.0,
                    "balance": 1200.0,
                    "units": 12.0,
                    "averagePrice": 100.0,
                    "currency": "PLN",
                    "comment": "initial",
                },
                occured_at=datetime(2026, 2, 1),
                version=1,
            )
        ]
    )

    payload, status = investment.create_investment_event_entry(
        {
            "streamId": str(stream.id),
            "eventType": "sell",
            "occuredAt": "2026-02-20",
            "units": 4.0,
            "totalValue": 400.0,
        }
    )

    assert status == 201
    assert payload["result"] == "Success"
    events = es.load(stream.id)
    assert events[1].event_type == "ETFSold"
    assert events[1].data["units"] == -4.0
    assert events[1].data["balance"] == 800.0


def test_create_etf_priced_event_sets_price_per_unit():
    stream = es.Stream(
        id=uuid.uuid4(),
        type="stocks",
        subtype="ETF",
        name="Test ETF",
        bank="Broker X",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    es.store(
        [
            es.Event(
                stream_type="stocks",
                stream_id=stream.id,
                event_type="ETFBought",
                data={
                    "totalValue": 1000.0,
                    "balance": 1000.0,
                    "units": 10.0,
                    "averagePrice": 100.0,
                    "currency": "PLN",
                    "comment": "initial",
                },
                occured_at=datetime(2026, 2, 1),
                version=1,
            )
        ]
    )

    payload, status = investment.create_investment_event_entry(
        {
            "streamId": str(stream.id),
            "eventType": "price_update",
            "occuredAt": "2026-02-22",
            "totalValue": 1500.0,
        }
    )

    assert status == 201
    assert payload["result"] == "Success"
    events = es.load(stream.id)
    assert events[1].event_type == "ETFPriced"
    assert events[1].data["pricePerUnit"] == 150.0
    assert events[1].data["balance"] == 1500.0


def test_create_treasury_bonds_bought_event_updates_balance():
    stream = es.Stream(
        id=uuid.uuid4(),
        type="investment",
        subtype="treasury_bonds",
        name="10-year Bonds",
        bank="Bank 1",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    payload, status = investment.create_investment_event_entry(
        {
            "streamId": str(stream.id),
            "eventType": "buy",
            "occuredAt": "2026-02-10",
            "units": 5.0,
            "totalValue": 500.0,
            "comment": "purchase",
        }
    )

    assert status == 201
    assert payload["result"] == "Success"
    events = es.load(stream.id)
    assert events[0].event_type == "TreasuryBondsBought"
    assert events[0].data["balance"] == 500.0
    assert events[0].data["pricePerUnit"] == 100.0


def test_create_treasury_bonds_matured_event_stores_negative_units():
    stream = es.Stream(
        id=uuid.uuid4(),
        type="investment",
        subtype="treasury_bonds",
        name="10-year Bonds",
        bank="Bank 1",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    es.store(
        [
            es.Event(
                stream_type="investment",
                stream_id=stream.id,
                event_type="TreasuryBondsBought",
                data={
                    "totalValue": 1000.0,
                    "balance": 1000.0,
                    "units": 10.0,
                    "pricePerUnit": 100.0,
                    "currency": "PLN",
                    "comment": "initial",
                },
                occured_at=datetime(2026, 2, 1),
                version=1,
            )
        ]
    )

    payload, status = investment.create_investment_event_entry(
        {
            "streamId": str(stream.id),
            "eventType": "sell",
            "occuredAt": "2026-02-20",
            "units": 4.0,
            "totalValue": 400.0,
        }
    )

    assert status == 201
    assert payload["result"] == "Success"
    events = es.load(stream.id)
    assert events[1].event_type == "TreasuryBondsMatured"
    assert events[1].data["units"] == -4.0
    assert events[1].data["balance"] == 600.0


def test_create_treasury_bonds_priced_event_sets_price_per_unit():
    stream = es.Stream(
        id=uuid.uuid4(),
        type="investment",
        subtype="treasury_bonds",
        name="10-year Bonds",
        bank="Bank 1",
        active=True,
        version=0,
        metadata={},
        labels={"wallet": "Personal"},
    )
    es.create([stream])

    es.store(
        [
            es.Event(
                stream_type="investment",
                stream_id=stream.id,
                event_type="TreasuryBondsBought",
                data={
                    "totalValue": 1000.0,
                    "balance": 1000.0,
                    "units": 10.0,
                    "pricePerUnit": 100.0,
                    "currency": "PLN",
                    "comment": "initial",
                },
                occured_at=datetime(2026, 2, 1),
                version=1,
            )
        ]
    )

    payload, status = investment.create_investment_event_entry(
        {
            "streamId": str(stream.id),
            "eventType": "price_update",
            "occuredAt": "2026-02-25",
            "totalValue": 1500.0,
        }
    )

    assert status == 201
    assert payload["result"] == "Success"
    events = es.load(stream.id)
    assert events[1].event_type == "TreasuryBondsPriced"
    assert events[1].data["pricePerUnit"] == 150.0
    assert events[1].data["balance"] == 1500.0
