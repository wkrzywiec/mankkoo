# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import scripts.data as dt


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

dane = [
    dict(
        x = [dt.date('01-01-2021'), dt.date('24-01-2021'), dt.date('30-01-2021'), dt.date('01-02-2021'), dt.date('27-02-2021')],
        y = [30230.21, 35830.88, 27850.21, 17640.21, 29106.86],
        name = "Bilans",
        marker=dict(
            color='rgb(55, 83, 109)'
        )
    )
]

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    ),

    dcc.Graph(
        figure=dict(
            data=dane,
            layout=dict(
                title='Total money',
                showlegend=False,
            margin=dict(l=40, r=0, t=40, b=30)
            )
        )
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)