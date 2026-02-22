"""Investment business logic module.

This module contains pure business logic functions for investment event processing,
validation, and derived value calculation. It handles ETF operations (buy, sell, price update)
and constructs proper event data structures.
"""


def map_event_type(event_type: str) -> str:
    """Map API event type to event name.

    Args:
        event_type: The event type from API ("buy", "sell", "price_update")

    Returns:
        The corresponding event name ("ETFBought", "ETFSold", "ETFPriced")

    Raises:
        ValueError: If event_type is not recognized
    """
    mapping = {
        "buy": "ETFBought",
        "sell": "ETFSold",
        "price_update": "ETFPriced",
    }

    if event_type not in mapping:
        raise ValueError(f"Unknown event type: {event_type}")

    return mapping[event_type]


def calculate_unit_price(total_value: float, units: float) -> float:
    """Calculate price per unit.

    Args:
        total_value: Total value of the transaction
        units: Number of units

    Returns:
        Price per unit (total_value / units)

    Raises:
        ValueError: If units is zero
    """
    if units == 0.0:
        raise ValueError("Units cannot be zero")

    return total_value / units


def validate_buy_event_data(units: float, total_value: float) -> None:
    """Validate buy event data.

    Args:
        units: Number of units to buy
        total_value: Total purchase price

    Raises:
        ValueError: If units or total_value is not greater than zero
    """
    if units <= 0.0:
        raise ValueError("Units must be greater than zero")

    if total_value <= 0.0:
        raise ValueError("Total value must be greater than zero")


def validate_sell_event_data(units: float, total_value: float) -> None:
    """Validate sell event data.

    Args:
        units: Number of units to sell
        total_value: Total sale price

    Raises:
        ValueError: If units or total_value is not greater than zero
    """
    if units <= 0.0:
        raise ValueError("Units must be greater than zero")

    if total_value <= 0.0:
        raise ValueError("Total value must be greater than zero")


def validate_price_update_data(price_per_unit: float) -> None:
    """Validate price update event data.

    Args:
        price_per_unit: Current market price per unit

    Raises:
        ValueError: If price_per_unit is not greater than zero
    """
    if price_per_unit <= 0.0:
        raise ValueError("Price per unit must be greater than zero")


def create_etf_bought_event_data(
    units: float, total_value: float, current_balance: float, comment: str = ""
) -> dict:
    """Create ETFBought event data.

    Args:
        units: Number of units purchased
        total_value: Total purchase price
        current_balance: Current portfolio balance before this purchase
        comment: Optional user comment

    Returns:
        Dictionary with event data structure:
        {
            "totalValue": float,
            "balance": float,
            "units": float,
            "averagePrice": float,
            "currency": str,
            "comment": str
        }
    """
    average_price = calculate_unit_price(total_value, units)
    new_balance = current_balance + total_value

    return {
        "totalValue": total_value,
        "balance": new_balance,
        "units": units,
        "averagePrice": average_price,
        "currency": "PLN",
        "comment": comment,
    }


def create_etf_sold_event_data(
    units: float, total_value: float, current_balance: float, comment: str = ""
) -> dict:
    """Create ETFSold event data.

    Args:
        units: Number of units sold (positive value)
        total_value: Total sale price
        current_balance: Current portfolio balance before this sale
        comment: Optional user comment

    Returns:
        Dictionary with event data structure:
        {
            "totalValue": float,
            "balance": float,
            "units": float,  # Negative value
            "averagePrice": float,
            "currency": str,
            "comment": str
        }
    """
    average_price = calculate_unit_price(total_value, units)
    new_balance = current_balance - total_value

    return {
        "totalValue": total_value,
        "balance": new_balance,
        "units": -units,  # Store as negative
        "averagePrice": average_price,
        "currency": "PLN",
        "comment": comment,
    }


def create_etf_priced_event_data(
    price_per_unit: float, current_units: float, comment: str = ""
) -> dict:
    """Create ETFPriced event data.

    Args:
        price_per_unit: Current market price per unit
        current_units: Current number of units in portfolio
        comment: Optional user comment

    Returns:
        Dictionary with event data structure:
        {
            "pricePerUnit": float,
            "balance": float,
            "currency": str,
            "comment": str
        }
    """
    balance = price_per_unit * current_units

    return {
        "pricePerUnit": price_per_unit,
        "balance": balance,
        "currency": "PLN",
        "comment": comment,
    }
