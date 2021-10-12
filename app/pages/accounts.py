from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as table
import app
import plotly.express as px

import scripts.main.importer.importer as importer
import scripts.main.models as models

from scripts.main.base_logger import log

def account_page():
    log.info("Loading accounts page")

    accounts_data = importer.load_data_from_file(models.FileType.ACCOUNT)
    accounts_data = accounts_data.iloc[::-1]
    accounts_names = list(accounts_data.groupby(['Bank', 'Account']).groups)

    account_tabs = []

    for account_name in accounts_names:
        single_account = accounts_data[(accounts_data['Bank'] == account_name[0]) & (accounts_data['Account'] == account_name[1])]
        single_account = single_account[['Date', 'Title', 'Details', 'Operation', 'Balance', 'Currency', 'Comment']]

        account_tab = __account_tab(single_account, account_name)
        account_tabs.append(account_tab)

    return html.Div(className='height-100 container main-body', children=[
        html.Div(className='row', children=[
            html.Div(className='col-4', children=[
                html.Label(htmlFor='bank-id', children=['Bank']),
                dcc.Dropdown(
                    id='bank-id',
                    options=[
                        {'label': 'Poland - ING', 'value': 'PL_ING'},
                        {'label': 'Poland - Millenium', 'value': 'PL_MILLENIUM'},
                        {'label': 'Mankkoo format', 'value': 'MANKKOO'}
                    ],
                    value='PL_MILLENIUM')
            ]),
            html.Div(className='col-2', children=[
                html.Label(htmlFor='account-type', children=['Account type']),
                dcc.Dropdown(
                    id='account-type',
                    options=[
                        {'label': 'Checking', 'value': 'checking'},
                        {'label': 'Savings', 'value': 'savings'}
                    ],
                    value='checking')
            ]),
            html.Div(className='col-4', children=[
                html.Label(htmlFor='account-name', children=['Account name']),
                dcc.Input(id='account-name', placeholder='Accunt name', type='text', style={'width': '100%'})
            ])
        ]),
        html.Div(className='row', children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files'),
                    " to upload account's files"
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False),
            html.Div(id='import-modal-wrapper', style={'display': 'none'})
        ]),
        html.Div(className='row', children=[
            dcc.Tabs(
                id="tabs-styled-with-inline",
                parent_className='accounts-tabs-container',
                children=account_tabs)
        ])
    ])


def __account_tab(account_data, account_name):
    full_account_name = account_name[0] + ' - ' + account_name[1]

    return dcc.Tab(label=full_account_name, selected_className='accounts-tab-selected', children=[

        html.Div(className='row', children=[
            dcc.Graph(figure=__account_chart(account_data))
        ]),

        table.DataTable(
            id=full_account_name + '-table',
            columns=[{"name": i, "id": i} for i in account_data],
            data=account_data.to_dict('records'),
            page_size=20,
            style_cell={
                'textAlign': 'left',
                'font-family': 'Rubik'},
            style_header={
                'backgroundColor': 'rgba(245, 214, 186, 0.7)',
                'font-family': 'Rubik',
                'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{Operation} > 0',
                        'column_id': 'Operation'
                    },
                    'backgroundColor': '#acc3a6'
                },
                {
                    'if': {
                        'filter_query': '{Operation} < 0',
                        'column_id': 'Operation'
                    },
                    'backgroundColor': '#cc5a71',
                    'color': 'white'
                }])
    ])

def __account_chart(account_data):
    account_data = account_data[['Date', 'Balance']]
    chart = px.line(account_data, x='Date', y='Balance', color_discrete_sequence=app.mankkoo_colors)
    chart.update_layout(
        font_family='Rubik'
    )
    return chart
