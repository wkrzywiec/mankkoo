import dash_html_components as html
import dash_core_components as dcc
from dash_table.Format import Format, Group, Scheme, Symbol
from dash_table import DataTable, FormatTemplate
import plotly.express as px
import plotly.graph_objects as go

import scripts.main.total as total
import scripts.main.data as dt
import app

data = dt.load_data()

total_money = total.total_money_data(data)

def main_page():
    return html.Div(className='height-100 container main-body', children=[

        html.Div(className='row', children=[
            html.Div(className='col-3', children=[
                html.Div(className='card card-indicator', children=[
                     html.Div(className='card-body card-body-indicator', children=[
                        html.Span('My Wealth', className='card-body-title'),
                        html.Span('{:,.2f} PLN'.format(total_money['Total'].sum()).replace(',', ' '))
                     ])
                ])
            ])
        ]),

        html.Div(className='row', children=[
            html.Div(className='col-4', children=[
                html.Div(className='card card-indicator', style={'height': '366px', 'width': '400px'}, children=[
                    html.Div(className='card-body card-body-plotly', children=[
                        html.Span('Wealth Distribution', className='card-body-title', style={'margin-bottom': '40px'}),
                        total_money_table(total_money)
                    ])
                ])
            ]),
            html.Div(className="col-5", children=[
                html.Div(className='card card-indicator', children=[
                    html.Div(className='card-body card-body-plotly', children=[
                        html.Span('Wealth Distribution', className='card-body-title', style={'margin-bottom': '20px'}),
                        html.Div(dcc.Graph(figure=total_money_pie(total_money)), style={'width': '400px'})
                    ])
                ])
            ])
        ]),

        html.Div(className='row', style={'padding-bottom': '50px'}, children=[
             html.Div(className='col-12', children=[
                html.Div(className='card card-indicator', children=[
                    html.Div(className='card-body card-body-plotly', children=[
                        html.Span('Wealth History', className='card-body-title'),
                        html.Div(dcc.Graph(figure=total_money_chart(data['total'])), style={'width': '1200px'})
                    ])
                ])
            ]),
        ])
    ])

def total_money_table(data):
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
                    symbol=Symbol.no)),
            dict(id='Percentage', name='Percentage', type='numeric', format=FormatTemplate.percentage(2))
        ],
        data=data.to_dict('records'),
        style_cell={
            'fontFamily': 'Rubik',
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
        style_as_list_view=True,
        fill_width=False
    )
    return table

def total_money_pie(data):
    data = data.drop(columns=['Percentage'])
    fig = go.Figure(data=[go.Pie(labels=data['Type'].tolist(), values=data['Total'].tolist(), hole=.4)])
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(colors=app.mankkoo_colors))
    fig.update_layout(
        autosize=False,
        width=400,
        height=300,
        margin=dict(l=50, r=50, b=0, t=0, pad=20),
        font_family='Rubik'
    )
    return fig

def total_money_chart(data):
    chart = px.line(data, x='Date', y='Total', color_discrete_sequence=app.mankkoo_colors)
    chart.update_layout(
        font_family='Rubik'
    )
    return chart
