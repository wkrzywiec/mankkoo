from datetime import date
from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Float, List
import mankkoo.database as db
import mankkoo.total as total

main_endpoints = APIBlueprint('main_endpoints', __name__, tag='Main Page')

class MainIndicators(Schema):
    savings = Float()
    debt = Float()
    lastMonthProfit = Float()
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
        'debt': None,
        'lastMonthProfit': last_month_income,
        'investments': None
    }

class SavingsDistribution(Schema):
    type = String()
    total = Float()
    percentage = Float()

@main_endpoints.route("/savings-distribution")
@main_endpoints.output(SavingsDistribution(many=True), status_code = 200)
@main_endpoints.doc(summary='Savings Distribution', description='Information about the distribution of wealth')
def savings_distribution():
    data = db.load_all()
    total_money = total.total_money_data(data).copy()
    total_money = total_money.rename(columns={'Total': 'total', 'Type': 'type', 'Percentage': 'percentage'})
    return total_money.to_dict('records')

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
    data = db.load_all()
    result = data['total_monthly']
    print(result)
    result['total'] = result.pop('Profit')
    result['date'] = result.pop('Date')
    return result.to_dict('list')