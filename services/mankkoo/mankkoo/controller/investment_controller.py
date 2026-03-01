from apiflask import APIBlueprint, Schema
from apiflask.fields import Boolean, Float, Integer, List, String

import mankkoo.views as views
from mankkoo.investment import investment_db
from mankkoo.investment.investment import create_investment_event_entry

investment_endpoints = APIBlueprint("investment_endpoints", __name__, tag="Investments")


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
    indicators = views.load_view(views.investment_indicators_key)
    if indicators is None:
        return {"result": "Failure", "details": "Indicators not available"}, 404
    return indicators


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
    return create_investment_event_entry(data)
