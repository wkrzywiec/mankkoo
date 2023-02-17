from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route("/indicators")
def indicators():
    return {
        'savings': 1000.12,
        'debt': 0.00,
        'lasyMonthProfit': -12.56,
        'investments': 0.00
    }

@main.route("/savings-distribution")
def savings_distribution():
    return {
        'total': 1000.12,
        'values': [0.00, 120.64],
        'keys': ['Checking Account', 'Savings Account', 'Cash', 'PPK', 'Investments', 'Stock']
    }

@main.route("/total-history")
def total_history():
    return {
        'date': ['2022-12-01'],
        'total': [0.00, 120.64]
    }

@main.route("/monthly-profits")
def monthly_profits():
    return {
        'date': ['2022-12'],
        'total': [0.00, 120.64]
    }