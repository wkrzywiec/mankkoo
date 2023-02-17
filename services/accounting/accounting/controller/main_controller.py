from flask import Blueprint

main_endpoints = Blueprint('main_endpoints', __name__)

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

@main_endpoints.route("/total-history")
def total_history():
    return {
        'date': ['2022-12-01'],
        'total': [0.00, 120.64]
    }

@main_endpoints.route("/monthly-profits")
def monthly_profits():
    return {
        'date': ['2022-12'],
        'total': [0.00, 120.64]
    }