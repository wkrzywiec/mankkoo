import pytest

from mankkoo.investment import investment


class TestEventTypeMapping:
    """Test event type mapping from API to event names"""

    def test_map_buy_event_type(self):
        # WHEN
        result = investment.map_event_type("buy")

        # THEN
        assert result == "ETFBought"

    def test_map_sell_event_type(self):
        # WHEN
        result = investment.map_event_type("sell")

        # THEN
        assert result == "ETFSold"

    def test_map_price_update_event_type(self):
        # WHEN
        result = investment.map_event_type("price_update")

        # THEN
        assert result == "ETFPriced"

    def test_map_invalid_event_type_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Unknown event type"):
            investment.map_event_type("unknown_type")


class TestCalculateUnitPrice:
    """Test unit price calculation"""

    def test_calculate_unit_price_with_valid_inputs(self):
        # WHEN
        result = investment.calculate_unit_price(total_value=1000.0, units=10.0)

        # THEN
        assert result == 100.0

    def test_calculate_unit_price_with_fractional_units(self):
        # WHEN
        result = investment.calculate_unit_price(total_value=1234.56, units=5.5)

        # THEN
        assert result == pytest.approx(224.465454, rel=1e-5)

    def test_calculate_unit_price_with_zero_units_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Units cannot be zero"):
            investment.calculate_unit_price(total_value=1000.0, units=0.0)


class TestValidateBuyEventData:
    """Test validation for buy event data"""

    def test_validate_buy_event_data_with_valid_inputs(self):
        # WHEN / THEN (should not raise)
        investment.validate_buy_event_data(units=10.0, total_value=1000.0)

    def test_validate_buy_event_data_with_zero_units_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Units must be greater than zero"):
            investment.validate_buy_event_data(units=0.0, total_value=1000.0)

    def test_validate_buy_event_data_with_negative_units_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Units must be greater than zero"):
            investment.validate_buy_event_data(units=-5.0, total_value=1000.0)

    def test_validate_buy_event_data_with_zero_total_value_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Total value must be greater than zero"):
            investment.validate_buy_event_data(units=10.0, total_value=0.0)

    def test_validate_buy_event_data_with_negative_total_value_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Total value must be greater than zero"):
            investment.validate_buy_event_data(units=10.0, total_value=-100.0)


class TestValidateSellEventData:
    """Test validation for sell event data"""

    def test_validate_sell_event_data_with_valid_inputs(self):
        # WHEN / THEN (should not raise)
        investment.validate_sell_event_data(units=5.0, total_value=500.0)

    def test_validate_sell_event_data_with_zero_units_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Units must be greater than zero"):
            investment.validate_sell_event_data(units=0.0, total_value=500.0)

    def test_validate_sell_event_data_with_negative_units_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Units must be greater than zero"):
            investment.validate_sell_event_data(units=-3.0, total_value=500.0)

    def test_validate_sell_event_data_with_zero_total_value_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Total value must be greater than zero"):
            investment.validate_sell_event_data(units=5.0, total_value=0.0)

    def test_validate_sell_event_data_with_negative_total_value_raises_error(self):
        # WHEN / THEN
        with pytest.raises(ValueError, match="Total value must be greater than zero"):
            investment.validate_sell_event_data(units=5.0, total_value=-100.0)


class TestValidatePriceUpdateData:
    """Test validation for price update event data"""

    def test_validate_price_update_data_with_valid_input(self):
        # WHEN / THEN (should not raise)
        investment.validate_price_update_data(price_per_unit=125.50)

    def test_validate_price_update_data_with_zero_price_raises_error(self):
        # WHEN / THEN
        with pytest.raises(
            ValueError, match="Price per unit must be greater than zero"
        ):
            investment.validate_price_update_data(price_per_unit=0.0)

    def test_validate_price_update_data_with_negative_price_raises_error(self):
        # WHEN / THEN
        with pytest.raises(
            ValueError, match="Price per unit must be greater than zero"
        ):
            investment.validate_price_update_data(price_per_unit=-50.0)


class TestCreateETFBoughtEventData:
    """Test ETFBought event data creation"""

    def test_create_etf_bought_event_data_with_basic_inputs(self):
        # WHEN
        result = investment.create_etf_bought_event_data(
            units=10.0, total_value=1000.0, current_balance=2000.0
        )

        # THEN
        assert result["units"] == 10.0
        assert result["totalValue"] == 1000.0
        assert result["averagePrice"] == 100.0  # 1000.0 / 10.0
        assert result["balance"] == 3000.0  # 2000.0 + 1000.0
        assert result["currency"] == "PLN"
        assert result["comment"] == ""

    def test_create_etf_bought_event_data_with_comment(self):
        # WHEN
        result = investment.create_etf_bought_event_data(
            units=5.5,
            total_value=550.0,
            current_balance=1000.0,
            comment="First purchase",
        )

        # THEN
        assert result["units"] == 5.5
        assert result["totalValue"] == 550.0
        assert result["averagePrice"] == 100.0  # 550.0 / 5.5
        assert result["balance"] == 1550.0  # 1000.0 + 550.0
        assert result["currency"] == "PLN"
        assert result["comment"] == "First purchase"

    def test_create_etf_bought_event_data_with_zero_current_balance(self):
        # WHEN
        result = investment.create_etf_bought_event_data(
            units=8.0, total_value=800.0, current_balance=0.0
        )

        # THEN
        assert result["balance"] == 800.0  # 0.0 + 800.0
        assert result["averagePrice"] == 100.0


class TestCreateETFSoldEventData:
    """Test ETFSold event data creation"""

    def test_create_etf_sold_event_data_with_basic_inputs(self):
        # WHEN
        result = investment.create_etf_sold_event_data(
            units=5.0, total_value=500.0, current_balance=2000.0
        )

        # THEN
        assert result["units"] == -5.0  # Negative for sold
        assert result["totalValue"] == 500.0
        assert result["averagePrice"] == 100.0  # 500.0 / 5.0
        assert result["balance"] == 1500.0  # 2000.0 - 500.0
        assert result["currency"] == "PLN"
        assert result["comment"] == ""

    def test_create_etf_sold_event_data_with_comment(self):
        # WHEN
        result = investment.create_etf_sold_event_data(
            units=3.25,
            total_value=325.0,
            current_balance=1000.0,
            comment="Partial sale",
        )

        # THEN
        assert result["units"] == -3.25  # Negative for sold
        assert result["totalValue"] == 325.0
        assert result["averagePrice"] == 100.0  # 325.0 / 3.25
        assert result["balance"] == 675.0  # 1000.0 - 325.0
        assert result["currency"] == "PLN"
        assert result["comment"] == "Partial sale"

    def test_create_etf_sold_event_data_selling_all(self):
        # WHEN
        result = investment.create_etf_sold_event_data(
            units=10.0, total_value=1200.0, current_balance=1200.0
        )

        # THEN
        assert result["balance"] == 0.0  # 1200.0 - 1200.0
        assert result["units"] == -10.0


class TestCreateETFPricedEventData:
    """Test ETFPriced event data creation"""

    def test_create_etf_priced_event_data_with_basic_inputs(self):
        # WHEN
        result = investment.create_etf_priced_event_data(
            price_per_unit=125.0, current_units=10.0
        )

        # THEN
        assert result["pricePerUnit"] == 125.0
        assert result["balance"] == 1250.0  # 125.0 * 10.0
        assert result["currency"] == "PLN"
        assert result["comment"] == ""

    def test_create_etf_priced_event_data_with_comment(self):
        # WHEN
        result = investment.create_etf_priced_event_data(
            price_per_unit=99.50, current_units=5.5, comment="Monthly revaluation"
        )

        # THEN
        assert result["pricePerUnit"] == 99.50
        assert result["balance"] == pytest.approx(547.25, rel=1e-5)  # 99.50 * 5.5
        assert result["currency"] == "PLN"
        assert result["comment"] == "Monthly revaluation"

    def test_create_etf_priced_event_data_with_zero_units(self):
        # WHEN
        result = investment.create_etf_priced_event_data(
            price_per_unit=100.0, current_units=0.0
        )

        # THEN
        assert result["balance"] == 0.0  # 100.0 * 0.0

    def test_create_etf_priced_event_data_with_fractional_price_and_units(self):
        # WHEN
        result = investment.create_etf_priced_event_data(
            price_per_unit=123.456, current_units=7.89
        )

        # THEN
        assert result["pricePerUnit"] == 123.456
        assert result["balance"] == pytest.approx(974.06784, rel=1e-5)  # 123.456 * 7.89
