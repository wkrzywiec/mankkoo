from apiflask import APIBlueprint, Schema
from apiflask.fields import Float
import mankkoo.views as views

investment_endpoints = APIBlueprint('investment_endpoints', __name__, tag='Investments')


class InvestmentIndicators(Schema):
    totalInvestments = Float()
    lastYearTotalResultsValue = Float()
    lastYearTotalResultsPercentage = Float()
    resultsVsInflation = Float()


@investment_endpoints.route("/indicators")
@investment_endpoints.output(InvestmentIndicators, status_code=200)
@investment_endpoints.doc(summary='Investment Indicators',
                          description='Key investment performance metrics including total investments, yearly results, and inflation comparison')
def investment_indicators():
    return views.load_view(views.investment_indicators_key)
