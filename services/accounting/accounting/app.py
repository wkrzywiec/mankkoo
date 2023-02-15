from flask import Flask

app = Flask(__name__)

@app.route("/main/indicators")
def main_indicators():
    return {
        'savings': 1000.12,
        'debt': 0.00,
        'lasyMonthProfit': -12.56,
        'investments': 0.00
    }

@app.route("/main/savings-distribution")
def main_indicators():
    return {
        'total': 1000.12,
        'values': [0.00, 120.64],
        'keys': ['Checking Account', 'Savings Account', 'Cash', 'PPK', 'Investments', 'Stock']
    }

@app.route("/main/total-history")
def main_indicators():
    return {
        'date': ['2022-12-01'],
        'total': [0.00, 120.64]
    }

@app.route("/main/monthly-profits")
def main_indicators():
    return {
        'date': ['2022-12'],
        'total': [0.00, 120.64]
    }