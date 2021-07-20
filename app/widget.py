from dash_table.Format import Format, Group, Scheme, Symbol
from dash_table import DataTable, FormatTemplate
import dash_html_components as html
import plotly.express as px


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

def total_money_pie(data):
    data = data.drop(columns=['Percentage'])
    pie = px.pie(data, values='Total', names='Type', title='Total Money distribution')
    pie.update_traces(textposition='inside', textinfo='percent+label')
    return pie

def total_money_chart(data):
    chart = px.line(data, x='Date', y='Total', title='Total money')
    return chart

def navbar():
    return html.Div(className='l-navbar', id='nav-bar', children=[
            html.Nav(className='nav', children=[
                html.Div(children=[
                    html.A(href='#', className='nav_logo', children=[
                        html.I(className='bx bx-layer nav_logo-icon'),
                        html.Span('mankkoo', className='nav_logo-name')
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='#', className='nav_link active', children=[
                            html.I(className='bx bx-grid-alt nav_icon'),
                            html.Span('Overview', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='#', className='nav_link', children=[
                            html.I(className='bx bx-euro nav_icon'),
                            html.Span('Accounts', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='#', className='nav_link', children=[
                            html.I(className='bx bx-briefcase nav_icon'),
                            html.Span('Investments', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='#', className='nav_link', children=[
                            html.I(className='bx bx-bar-chart nav_icon'),
                            html.Span('Stock', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='#', className='nav_link', children=[
                            html.I(className='bx bx-medal nav_icon'),
                            html.Span('Retirement', className='nav_name')
                        ])
                    ])
                ])
            ])
    ])
