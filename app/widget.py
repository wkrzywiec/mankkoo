from dash_table.Format import Format, Group, Scheme, Symbol
from dash_table import DataTable, FormatTemplate
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import logging as log

mankkoo_colors = ['#A40E4C', '#ACC3A6', '#F5D6BA', '#F49D6E', '#27474E', '#BEB8EB', '#6BBF59', '#C2E812', '#5299D3']

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
    # pie = px.pie(data, values='Total', names='Type')  
    fig = go.Figure(data=[go.Pie(labels=data['Type'].tolist(), values=data['Total'].tolist(), hole=.4)])
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(colors=mankkoo_colors))
    fig.update_layout(
        autosize=False,
        width=400,
        height=300,
        margin=dict(l=50, r=50, b=0, t=0, pad=20),
        font_family='Rubik'
    )
    # pie.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
    return fig

def total_money_chart(data):
    chart = px.line(data, x='Date', y='Total', color_discrete_sequence=mankkoo_colors)
    chart.update_layout(
        font_family='Rubik'
    )
    return chart

def navbar(pathname: str):

    navbar = html.Div(className='l-navbar', id='nav-bar', children=[
            html.Nav(className='nav', children=[
                html.Div(children=[
                    html.A(href='/', className='nav_logo', children=[
                        html.I(className='bx bx-layer nav_logo-icon'),
                        html.Span('mankkoo', className='nav_logo-name')
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/', className='nav_link', children=[
                            html.I(className='bx bx-grid-alt nav_icon'),
                            html.Span('Overview', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/accounts', className='nav_link', children=[
                            html.I(className='bx bx-euro nav_icon'),
                            html.Span('Accounts', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/investments', className='nav_link', children=[
                            html.I(className='bx bx-briefcase nav_icon'),
                            html.Span('Investments', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/stocks', className='nav_link', children=[
                            html.I(className='bx bx-bar-chart nav_icon'),
                            html.Span('Stock', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/retirement', className='nav_link', children=[
                            html.I(className='bx bx-medal nav_icon'),
                            html.Span('Retirement', className='nav_name')
                        ])
                    ])
                ])
            ])
    ])

    for nav in navbar.children[0].children[0].children:
        if nav.className == 'nav_list':
            if nav.children[0].href == pathname:
                nav.children[0].className = 'nav_link active'

    return navbar
