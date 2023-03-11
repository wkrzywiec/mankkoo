from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Float, List

main_endpoints = APIBlueprint('main_endpoints', __name__, tag='Main Page')

class MainIndicators(Schema):
    savings = Float()
    debt = Float()
    lasyMonthProfit = Float()
    investments = Float()

@main_endpoints.route("/indicators")
@main_endpoints.output(MainIndicators, status_code = 200)
@main_endpoints.doc(summary='Main Indicators', description='Key indicators of a total wealth')
def indicators():
    return {
        'savings': 1000.12,
        'debt': 0.00,
        'lasyMonthProfit': -12.56,
        'investments': 0.00
    }

class SavingsDistribution(Schema):
    total = Float()
    keys = List(String())
    values = List(Float())

@main_endpoints.route("/savings-distribution")
@main_endpoints.output(SavingsDistribution, status_code = 200)
@main_endpoints.doc(summary='Savings Distribution', description='Information about the distribution of wealth')
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
@main_endpoints.doc(summary='Total History', description='A history of a total wealth in each day')
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
@main_endpoints.doc(summary='Monthly Profits', description='A history of a monthly profit and loss statements')
def monthly_profits():
    return {
        'date': ['2022-12'],
        'total': [120.64]
    }