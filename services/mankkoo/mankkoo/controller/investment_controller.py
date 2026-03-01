from apiflask import APIBlueprint, Schema
from apiflask.fields import Boolean, Float, Integer, List, String

import mankkoo.views as views
from mankkoo.investment import investment_db

investment_endpoints = APIBlueprint("investment_endpoints", __name__, tag="Investments")


def _as_float(value: float | int | str) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(" ", "").replace(",", ".")
        if not cleaned:
            raise ValueError("Numeric value cannot be empty")
        return float(cleaned)
    raise TypeError(f"Unsupported numeric value type: {type(value)}")


class InvestmentIndicators(Schema):
    totalInvestments = Float()
    lastYearTotalResultsValue = Float()
    lastYearTotalResultsPercentage = Float()
    resultsVsInflation = Float()


@investment_endpoints.route("/indicators")
@investment_endpoints.output(InvestmentIndicators, status_code=200)
@investment_endpoints.doc(
    summary="Investment Indicators",
    description="Key investment performance metrics including total investments, yearly results, and inflation comparison",
)
def investment_indicators():
    return views.load_view(views.investment_indicators_key)


class WalletsResponse(Schema):
    wallets = List(String())


@investment_endpoints.route("/wallets")
@investment_endpoints.output(WalletsResponse, status_code=200)
@investment_endpoints.doc(
    summary="Available Wallets",
    description="List of all unique wallets assigned to any stream",
)
def get_wallets():
    wallets = investment_db.load_wallets()
    return {"wallets": wallets}


class InvestmentsQuery(Schema):
    active = Boolean(
        required=False,
        description="Filter by active/inactive investments. 'true' or 'false'.",
    )
    wallet = String(required=False, description="Filter by wallet label.")


class InvestmentStreamResponse(Schema):
    id = String()
    name = String()
    investmentType = String()
    subtype = String()
    balance = Float()


@investment_endpoints.route("")
@investment_endpoints.input(InvestmentsQuery, location="query")
@investment_endpoints.output(InvestmentStreamResponse(many=True), status_code=200)
@investment_endpoints.doc(
    summary="All Investments",
    description=(
        "Fetch all investments (streams of type investment, stocks, or account with accountType=savings). "
        "Supports filtering by active/inactive and wallet."
    ),
)
def get_all_investments(query_data):
    active = query_data.get("active")
    wallet = query_data.get("wallet")
    return investment_db.load_investments(active=active, wallet=wallet)


class InvestmentTransaction(Schema):
    occuredAt = String()
    eventType = String()
    unitsCount = Float(allow_none=True)
    pricePerUnit = Float(allow_none=True)
    totalValue = Float(allow_none=True)
    balance = Float(allow_none=True)
    comment = String(allow_none=True)


@investment_endpoints.route("/transactions/<string:investment_id>")
@investment_endpoints.output(InvestmentTransaction(many=True), status_code=200)
@investment_endpoints.doc(
    summary="Investment Transactions",
    description="List all transactions for a given investment UUID, ordered by version desc.",
)
def get_investment_transactions(investment_id):
    transactions = investment_db.load_investment_transactions(investment_id)
    return transactions


# ============================================================================
# POST /api/investments/events - Create Investment Event
# ============================================================================


class InvestmentEventRequest(Schema):
    streamId = String(required=True, description="UUID of the investment stream")
    eventType = String(
        required=True, description="Event type: 'buy', 'sell', or 'price_update'"
    )
    occuredAt = String(
        required=True, description="Date when event occurred (ISO format)"
    )
    units = Float(required=False, description="Number of units (required for buy/sell)")
    totalValue = Float(
        required=True,
        description="Total value in PLN (required for buy/sell and price_update)",
    )
    comment = String(required=False, load_default="", description="Optional comment")


class InvestmentEventResponse(Schema):
    result = String()
    eventId = String()
    streamVersion = Integer()
    details = String(required=False)


@investment_endpoints.route("/events", methods=["POST"])
@investment_endpoints.input(InvestmentEventRequest)
@investment_endpoints.output(InvestmentEventResponse, status_code=201)
@investment_endpoints.doc(
    summary="Create Investment Event",
    description="Create a new investment event (buy, sell, or price update) for a stream",
)
def create_investment_event(data):
    import traceback
    from datetime import datetime
    from uuid import UUID

    import mankkoo.event_store as es
    from mankkoo.base_logger import log
    from mankkoo.investment.investment import (
        create_etf_bought_event_data,
        create_etf_priced_event_data,
        create_etf_sold_event_data,
        map_event_type,
        validate_buy_event_data,
        validate_price_update_data,
        validate_sell_event_data,
    )

    try:
        # 1. Extract request data
        stream_id = data.get("streamId")
        event_type = data.get("eventType")
        occured_at_str = data.get("occuredAt")
        units = data.get("units")
        total_value = data.get("totalValue")
        comment = data.get("comment", "")

        # 2. Validate required fields based on event type
        if event_type == "buy":
            if units is None or total_value is None:
                return {
                    "result": "Failure",
                    "details": "Missing required fields for buy event",
                }, 400
            validate_buy_event_data(units, total_value)
        elif event_type == "sell":
            if units is None or total_value is None:
                return {
                    "result": "Failure",
                    "details": "Missing required fields for sell event",
                }, 400
            validate_sell_event_data(units, total_value)
        elif event_type != "price_update":
            return {
                "result": "Failure",
                "details": f"Invalid event type: {event_type}",
            }, 400

        # 3. Load stream and verify it exists
        stream = es.get_stream_by_id(stream_id)
        if stream is None:
            return {"result": "Failure", "details": "Stream not found"}, 404

        # 4. Verify stream type is investment or stocks
        if stream.type not in ["investment", "stocks"]:
            return {
                "result": "Failure",
                "details": f"Invalid stream type: {stream.type}. Must be investments or stocks",
            }, 400

        # 5. Get current stream state (balance, units) from latest events
        current_balance = 0.0
        current_units = 0.0
        events = es.load(stream_id)

        # Sort events by version to ensure correct balance calculation
        # Events must be processed in order to get accurate current state
        events.sort(key=lambda e: e.version)

        for event in events:
            event_data = event.data
            if "balance" in event_data:
                current_balance = _as_float(event_data["balance"])
            if "units" in event_data:
                current_units += _as_float(event_data["units"])

        # For sell events, validate user has enough units
        if event_type == "sell" and units > current_units:
            return {
                "result": "Failure",
                "details": "Cannot sell more units than currently owned",
            }, 400

        if event_type == "price_update":
            validate_price_update_data(total_value, current_units)

        # 6. Map event type to event name
        event_name = map_event_type(event_type)

        # 7. Create event data using business logic functions
        event_data = {}
        if event_type == "buy":
            event_data = create_etf_bought_event_data(
                units, total_value, current_balance, comment
            )
        elif event_type == "sell":
            event_data = create_etf_sold_event_data(
                units, total_value, current_balance, comment
            )
        elif event_type == "price_update":
            event_data = create_etf_priced_event_data(
                total_value, current_units, comment
            )

        # 8. Parse occuredAt date
        occured_at = datetime.fromisoformat(occured_at_str)

        # 9. Create Event object with next version
        next_version = stream.version + 1
        event = es.Event(
            stream_type=stream.type,
            stream_id=UUID(stream_id),
            event_type=event_name,
            data=event_data,
            occured_at=occured_at,
            version=next_version,
        )

        # 10. Store event in database
        es.store([event])

        log.info(
            f"Created {event_name} event for stream {stream_id} with version {next_version}"
        )

        # 11. Return success response
        return {
            "result": "Success",
            "eventId": str(event.id),
            "streamVersion": next_version,
        }, 201

    except ValueError as ex:
        log.error(f"Validation error: {ex}", exc_info=True)
        return {"result": "Failure", "details": str(ex)}, 400
    except Exception as ex:
        log.error(
            f"Failed to create investment event: {ex}, traceback: {traceback.format_exc()}"
        )
        return {"result": "Failure", "details": str(ex)}, 500
