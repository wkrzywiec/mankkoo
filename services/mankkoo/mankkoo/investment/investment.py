"""Investment business logic module.

This module contains business logic functions for investment event processing,
validation, and derived value calculation. It handles ETF operations (buy, sell, price
update) along with treasury bonds operations (buy, sell, matured) and constructs proper
event data structures.
"""

from datetime import datetime
from typing import Any, Dict, Tuple
from uuid import UUID

import mankkoo.event_store as es
from mankkoo.base_logger import log


def _as_float(value: float | int | str) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(" ", "").replace(",", ".")
        if not cleaned:
            raise ValueError("Numeric value cannot be empty")
        return float(cleaned)
    raise TypeError(f"Unsupported numeric value type: {type(value)}")


def __map_event_type(stream_subtype: str, event_type: str) -> str:
    mapping_by_subtype = {
        "ETF": {
            "buy": "ETFBought",
            "sell": "ETFSold",
            "price_update": "ETFPriced",
        },
        "treasury_bonds": {
            "buy": "TreasuryBondsBought",
            "sell": "TreasuryBondsMatured",
            "price_update": "TreasuryBondsPriced",
        },
    }

    if stream_subtype not in mapping_by_subtype:
        raise ValueError(f"Unsupported investment subtype: {stream_subtype}")

    mapping = mapping_by_subtype[stream_subtype]
    if event_type not in mapping:
        raise ValueError(
            f"Unsupported event type: {event_type} for subtype: {stream_subtype}"
        )

    return mapping[event_type]


def __calculate_unit_price(total_value: float, units: float) -> float:
    if units == 0.0:
        raise ValueError("Units cannot be zero")

    return total_value / units


def __validate_buy_event_data(units: float, total_value: float) -> None:
    if units <= 0.0:
        raise ValueError("Units must be greater than zero")

    if total_value <= 0.0:
        raise ValueError("Total value must be greater than zero")


def __validate_sell_event_data(units: float, total_value: float) -> None:
    if units <= 0.0:
        raise ValueError("Units must be greater than zero")

    if total_value <= 0.0:
        raise ValueError("Total value must be greater than zero")


def __validate_price_update_data(total_value: float, current_units: float) -> None:
    if total_value <= 0.0:
        raise ValueError("Total value must be greater than zero")

    if current_units <= 0.0:
        raise ValueError("Cannot update price without owned units")


def __create_etf_bought_event_data(
    units: float, total_value: float, current_balance: float, comment: str = ""
) -> dict:
    average_price = __calculate_unit_price(total_value, units)
    new_balance = current_balance + total_value

    return {
        "totalValue": total_value,
        "balance": new_balance,
        "units": units,
        "averagePrice": average_price,
        "currency": "PLN",
        "comment": comment,
    }


def __create_etf_sold_event_data(
    units: float, total_value: float, current_balance: float, comment: str = ""
) -> dict:
    average_price = __calculate_unit_price(total_value, units)
    new_balance = current_balance - total_value

    return {
        "totalValue": total_value,
        "balance": new_balance,
        "units": -units,  # Store as negative
        "averagePrice": average_price,
        "currency": "PLN",
        "comment": comment,
    }


def __create_etf_priced_event_data(
    total_value: float, current_units: float, comment: str = ""
) -> dict:
    if total_value <= 0.0:
        raise ValueError("Total value must be greater than zero")

    if current_units <= 0.0:
        raise ValueError("Current units must be greater than zero")

    price_per_unit = total_value / current_units
    balance = total_value

    return {
        "pricePerUnit": price_per_unit,
        "balance": balance,
        "currency": "PLN",
        "comment": comment,
    }


def __create_treasury_bonds_bought_event_data(
    units: float, total_value: float, current_balance: float, comment: str = ""
) -> dict:
    price_per_unit = __calculate_unit_price(total_value, units)
    new_balance = current_balance + total_value

    return {
        "totalValue": total_value,
        "balance": new_balance,
        "units": units,
        "pricePerUnit": price_per_unit,
        "currency": "PLN",
        "comment": comment,
    }


def __create_treasury_bonds_sold_event_data(
    units: float, total_value: float, current_balance: float, comment: str = ""
) -> dict:
    price_per_unit = __calculate_unit_price(total_value, units)
    new_balance = current_balance - total_value

    return {
        "totalValue": total_value,
        "balance": new_balance,
        "units": -units,
        "pricePerUnit": price_per_unit,
        "currency": "PLN",
        "comment": comment,
    }


def __create_treasury_bonds_priced_event_data(
    total_value: float, current_units: float, comment: str = ""
) -> dict:
    if total_value <= 0.0:
        raise ValueError("Total value must be greater than zero")

    if current_units <= 0.0:
        raise ValueError("Current units must be greater than zero")

    price_per_unit = total_value / current_units

    return {
        "balance": total_value,
        "units": current_units,
        "pricePerUnit": price_per_unit,
        "currency": "PLN",
        "comment": comment,
    }

def create_investment_event_entry(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    try:
        stream_id = data.get("streamId")
        event_type = data.get("eventType")
        occured_at_str = data.get("occuredAt")
        units = data.get("units")
        total_value = data.get("totalValue")
        comment = data.get("comment", "")

        if not stream_id:
            return {"result": "Failure", "details": "Stream id is required"}, 400

        if not event_type:
            return {"result": "Failure", "details": "Event type is required"}, 400

        if not occured_at_str:
            return {"result": "Failure", "details": "Occured date is required"}, 400

        stream_id_str = str(stream_id)
        event_type_str = str(event_type)
        occured_at_value = str(occured_at_str)

        stream = es.get_stream_by_id(stream_id_str)
        if stream is None:
            return {"result": "Failure", "details": "Stream not found"}, 404

        if stream.type not in ["investment", "stocks"]:
            return {
                "result": "Failure",
                "details": f"Invalid stream type: {stream.type}. Must be investments or stocks",
            }, 400

        if stream.subtype not in {"ETF", "treasury_bonds"}:
            return {
                "result": "Failure",
                "details": f"Unsupported investment subtype: {stream.subtype}",
            }, 400

        units_value = float(units) if units is not None else None
        total_value_value = float(total_value) if total_value is not None else None
        units_value_float: float | None = None
        total_value_float: float | None = None

        current_balance = 0.0
        current_units = 0.0
        events = es.load(UUID(stream_id_str))
        events.sort(key=lambda e: e.version)

        for event in events:
            event_data = event.data
            if "balance" in event_data:
                current_balance = _as_float(event_data["balance"])
            if "units" in event_data:
                current_units += _as_float(event_data["units"])

        if event_type_str in {"buy", "sell"}:
            if units is None or total_value is None:
                return {
                    "result": "Failure",
                    "details": "Missing required fields for buy/sell event",
                }, 400
            if units_value is None or total_value_value is None:
                return {
                    "result": "Failure",
                    "details": "Missing required fields for buy/sell event",
                }, 400
            units_value_float = float(units_value)
            total_value_float = float(total_value_value)
            if event_type_str == "buy":
                __validate_buy_event_data(units_value_float, total_value_float)
            else:
                __validate_sell_event_data(units_value_float, total_value_float)
        elif event_type_str == "price_update":
            if total_value is None:
                return {
                    "result": "Failure",
                    "details": "Missing required fields for price update event",
                }, 400
            if total_value_value is None:
                return {
                    "result": "Failure",
                    "details": "Missing required fields for price update event",
                }, 400
            total_value_float = float(total_value_value)
            __validate_price_update_data(total_value_float, current_units)
        else:
            return {
                "result": "Failure",
                "details": f"Invalid event type: {event_type_str}",
            }, 400

        if (
            event_type_str == "sell"
            and units_value_float is not None
            and units_value_float > current_units
        ):
            return {
                "result": "Failure",
                "details": "Cannot sell more units than currently owned",
            }, 400

        try:
            event_name = __map_event_type(stream.subtype, event_type_str)
        except ValueError as ex:
            return {"result": "Failure", "details": str(ex)}, 400

        if stream.subtype == "treasury_bonds":
            if event_type_str == "price_update":
                if total_value_float is None:
                    return {
                        "result": "Failure",
                        "details": "Missing required fields for price update event",
                    }, 400
                event_data = __create_treasury_bonds_priced_event_data(
                    total_value_float, current_units, comment
                )
            else:
                if units_value_float is None or total_value_float is None:
                    return {
                        "result": "Failure",
                        "details": "Missing required fields for buy/sell event",
                    }, 400
                if event_type_str == "buy":
                    event_data = __create_treasury_bonds_bought_event_data(
                        units_value_float, total_value_float, current_balance, comment
                    )
                else:
                    event_data = __create_treasury_bonds_sold_event_data(
                        units_value_float, total_value_float, current_balance, comment
                    )
        else:
            if event_type_str == "buy":
                if units_value_float is None or total_value_float is None:
                    return {
                        "result": "Failure",
                        "details": "Missing required fields for buy event",
                    }, 400
                event_data = __create_etf_bought_event_data(
                    units_value_float, total_value_float, current_balance, comment
                )
            elif event_type_str == "sell":
                if units_value_float is None or total_value_float is None:
                    return {
                        "result": "Failure",
                        "details": "Missing required fields for sell event",
                    }, 400
                event_data = __create_etf_sold_event_data(
                    units_value_float, total_value_float, current_balance, comment
                )
            else:
                if total_value_float is None:
                    return {
                        "result": "Failure",
                        "details": "Missing required fields for price update event",
                    }, 400
                event_data = __create_etf_priced_event_data(
                    total_value_float, current_units, comment
                )

        occured_at = datetime.fromisoformat(occured_at_value)
        next_version = stream.version + 1
        event = es.Event(
            stream_type=stream.type,
            stream_id=UUID(stream_id),
            event_type=event_name,
            data=event_data,
            occured_at=occured_at,
            version=next_version,
        )

        es.store([event])

        log.info(
            f"Created {event_name} event for stream {stream_id} with version {next_version}"
        )

        return {
            "result": "Success",
            "eventId": str(event.id),
            "streamVersion": next_version,
        }, 201

    except ValueError as ex:
        log.error(f"Validation error: {ex}", exc_info=True)
        return {"result": "Failure", "details": str(ex)}, 400
    except Exception as ex:
        import traceback

        log.error(
            f"Failed to create investment event: {ex}, traceback: {traceback.format_exc()}"
        )
        return {"result": "Failure", "details": str(ex)}, 500
