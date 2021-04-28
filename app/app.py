# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_table.Format import Format, Group, Scheme, Symbol
from dash_table import DataTable, FormatTemplate
import plotly.express as px
import pandas as pd
import scripts.main.data as dt


def __total_money_table(data):
    table = DataTable(
        id='total_money_table',
        columns=[
            dict(id='Type', name='Type'),
            dict(id='Total', name='Total', type='numeric', format=Format(
                    scheme=Scheme.fixed, 
                    precision=2,
                    group=Group.yes,
                    groups=3,
                    group_delimiter=' ',
                    decimal_delimiter=',',
                    symbol=Symbol.no)
                    ),
            dict(id='Percentage', name='Percentage', type='numeric', format=FormatTemplate.percentage(2))
        ],
        data=data.to_dict('records'),
        style_cell={
            'textAlign': 'right',
            'height': 'auto',
            # all three widths are needed
            'minWidth': '120px', 'width': '120px', 'maxWidth': '120px',
            'whiteSpace': 'normal'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'Type'},
                'textAlign': 'left'
            },
            
        ],
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{{Total}} = {}'.format(data['Total'].sum())
                },
                'color': 'tomato',
                'textDecoration': 'underline',
                'fontWeight': 'bold'
            }
        ],
        style_as_list_view=True,
        fill_width=False
    )
    return table

def __total_money_pie(data):
    data = data.drop(columns=['Percentage'])
    pie = px.pie(data, values='Total', names='Type',
             title='Total Money distribution')
    pie.update_traces(textposition='inside', textinfo='percent+label')
    return pie

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = dt.load_data()

total_money = dt.total_money_data(data)
total_table = __total_money_table(total_money)
total_pie = __total_money_pie(total_money)

# print(px.data.gapminder().query("year == 2007").query("continent == 'Americas'"))
# TODO add total money cell

# total_chart_data = data['account'][['Date', 'Balance']]
# fig = px.line(total_chart_data, x='Date', y='Balance', title='Balance')

app.layout = html.Div(children=[
    html.H1(children='mankkoo'),

    html.Div(children='''
        your personal finance dashboard
    '''),
    html.Div([
        html.Div([total_table], className="six columns"),
        html.Div([dcc.Graph(figure=total_pie)], className="six columns")
        ], className="row")

    # dcc.Graph(figure=fig) 
# )
])


if __name__ == '__main__':
    app.run_server(debug=True)