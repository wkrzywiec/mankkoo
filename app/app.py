# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import widget
import pandas as pd
import scripts.main.data as dt
import scripts.main.total as total
import scripts.main.config as config
import plotly.express as px


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = dt.load_data()

total_money = total.total_money_data(data)
total_table = widget.total_money_table(total_money)
total_pie = widget.total_money_pie(total_money)

config.init_data_folder()

# print(px.data.gapminder().query("year == 2007").query("continent == 'Americas'"))
# print(px.data.gapminder().query("country=='Canada'"))
# TODO add total money cell

# total_chart_data = data['account'][['Date', 'Balance']]
# fig = px.line(total_chart_data, x='Date', y='Balance', title='Balance')

app.layout = html.Div(children=[
    html.H1(children='mankkoo'),

    html.Div(children='''
        your personal finance dashboard
    '''),
    html.Div(children='''
        total money: {:,.2f} PLN
    '''.format(total_money['Total'].sum()).replace(',', ' ')),
    html.Div([
        html.Div([total_table], className="six columns"),
        html.Div([dcc.Graph(figure=total_pie)], className="six columns")
        ], className="row")

    # dcc.Graph(figure=fig) 
# )
])


if __name__ == '__main__':
    app.run_server(debug=True)