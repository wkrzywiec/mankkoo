from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Float, List

main_endpoints = APIBlueprint('main_endpoints', __name__)


@main_endpoints.route("/indicators")
def indicators():
    return {
        'savings': 1000.12,
        'debt': 0.00,
        'lasyMonthProfit': -12.56,
        'investments': 0.00
    }

@main_endpoints.route("/savings-distribution")
def savings_distribution():
    return {
        'total': 1000.12,
        'values': [0.00, 120.64],
        'keys': ['Checking Account', 'Savings Account', 'Cash', 'PPK', 'Investments', 'Stock']
    }

class TotalHistoryPerDay(Schema):
    date = List(String(), required=True)
    total = List(Float(), required=True)

@main_endpoints.route("/total-history")
@main_endpoints.output(TotalHistoryPerDay, status_code = 200)
def total_history():
    return {
        'date': ['2022-12-01'],
        'total': [120.64]
    }

class TotalMonthlyProfits(Schema):
    date = List(String(), required=True)
    total = List(Float(), required=True)

@main_endpoints.route("/monthly-profits")
@main_endpoints.output(TotalMonthlyProfits, status_code = 200)
def monthly_profits():
    return {
        'date': ['2022-12'],
        'total': [120.64]
    }