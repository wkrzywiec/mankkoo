import pytest

from mankkoo.investment import investment


def test_map_event_type_happy_path():
    assert investment.map_event_type("ETF", "buy") == "ETFBought"
    assert (
        investment.map_event_type("treasury_bonds", "price_update")
        == "TreasuryBondsPriced"
    )


def test_map_event_type_invalid_raises_value_error():
    with pytest.raises(ValueError):
        investment.map_event_type("ETF", "bonus")


def test_calculate_unit_price_returns_ratio():
    assert investment.calculate_unit_price(1000.0, 10.0) == 100.0


def test_calculate_unit_price_rejects_zero_units():
    with pytest.raises(ValueError):
        investment.calculate_unit_price(1000.0, 0.0)


def test_validate_buy_event_data_allows_positive_values():
    investment.validate_buy_event_data(units=10.0, total_value=500.0)


def test_validate_buy_event_data_rejects_zero_units():
    with pytest.raises(ValueError, match="Units must be greater than zero"):
        investment.validate_buy_event_data(units=0.0, total_value=500.0)


def test_validate_sell_event_data_allows_positive_values():
    investment.validate_sell_event_data(units=5.0, total_value=250.0)


def test_validate_sell_event_data_rejects_zero_total_value():
    with pytest.raises(ValueError, match="Total value must be greater than zero"):
        investment.validate_sell_event_data(units=5.0, total_value=0.0)


def test_validate_price_update_data_requires_units():
    with pytest.raises(ValueError, match="Cannot update price without owned units"):
        investment.validate_price_update_data(total_value=100.0, current_units=0.0)


def test_validate_price_update_data_allows_positive_flow():
    investment.validate_price_update_data(total_value=1250.0, current_units=10.0)


def test_create_etf_bought_event_data_updates_balance():
    data = investment.create_etf_bought_event_data(
        units=10.0, total_value=1000.0, current_balance=2000.0, comment="initial"
    )

    assert data["balance"] == 3000.0
    assert data["averagePrice"] == 100.0
    assert data["comment"] == "initial"


def test_create_etf_sold_event_data_stores_negative_units():
    data = investment.create_etf_sold_event_data(
        units=4.0, total_value=400.0, current_balance=1200.0
    )

    assert data["units"] == -4.0
    assert data["balance"] == 800.0


def test_create_etf_priced_event_data_sets_price_per_unit():
    data = investment.create_etf_priced_event_data(total_value=1500.0, current_units=10.0)

    assert data["pricePerUnit"] == 150.0
    assert data["balance"] == 1500.0
