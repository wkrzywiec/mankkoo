from datetime import date
from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Float, List
import accounting.database as db
import accounting.total as total

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
    data = db.load_all()
    total_money = total.total_money_data(data)['Total'].sum()
    last_month_income = total.last_month_income(db.load_total(), date.today())
    return {
        'savings': total_money,
        'debt': 0.00,
        'lasyMonthProfit': last_month_income,
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
    data = db.load_all()
    total_money = total.total_money_data(data)
    
    result = total_money.to_dict('list')
    result['keys'] = result.pop('Type')
    result['values'] = result.pop('Total')
    result['total'] = total_money['Total'].sum()
    return result

class TotalHistoryPerDay(Schema):
    date = List(String(), required=True)
    total = List(Float(), required=True)

@main_endpoints.route("/total-history")
@main_endpoints.output(TotalHistoryPerDay, status_code = 200)
@main_endpoints.doc(summary='Total History', description='A history of a total wealth in each day')
def total_history():
    data = db.load_all()
    result = data['total']
    result['total'] = result.pop('Total')
    result['date'] = result.pop('Date')
    return result.to_dict('list')

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