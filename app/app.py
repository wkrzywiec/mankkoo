# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import scripts.main.data as dt


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = dt.load_data()
total_chart_data = data['account'][['Date', 'Balance']]

fig = px.line(total_chart_data, x='Date', y='Balance', title='Balance')

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(figure=fig),

    # dash_table.DataTable(
    #     data=df.to_dict('records'),
    #     columns=[{'id': c, 'name': c} for c in df.columns],
    #     style_cell_conditional=[
    #         {
    #             'if': {'column_id': c},
    #             'textAlign': 'left'
    #         } for c in ['Date', 'Region']
    # ],

    # style_as_list_view=True,
# )
])


if __name__ == '__main__':
    app.run_server(debug=True)