import dash_core_components as dcc
import dash_html_components as html
import dash_table as table
import app
import plotly.express as px

import scripts.main.database as db
import scripts.main.config as config
import scripts.main.ui as ui

from scripts.main.base_logger import log

def account_page():
    log.info("Loading accounts page")

    global_config = config.load_global_config()
    user_config = config.load_user_config()
    bank_ids = ui.decode_bank_ids(global_config['accounts']['importers'])

    accounts_data = db.load_accounts()
    accounts_data = accounts_data.iloc[::-1]
    accounts = user_config['accounts']['definitions']

    accout_importers = []
    account_tabs = []

    for acc in accounts:
        acc_name = str(acc['bank']) + ' - ' + str(acc['name'])
        if acc_name in user_config['accounts']['ui']['hide_accounts'] or acc['active'] == False:
            continue

        acc_id = acc['id']

        accout_importers.append({'label': f'{acc_name} ({acc_id})', 'value': acc_id})
        single_account = accounts_data[accounts_data['Account'] == acc['id']]
        single_account = single_account[['Date', 'Title', 'Details', 'Operation', 'Balance', 'Currency', 'Comment']]

        account_tab = __account_tab(single_account, acc_name)
        account_tabs.append(account_tab)

    return html.Div(className='height-100 container main-body', children=[
        html.H1('Accounts', className='title'),
        html.Div(className='row', children=[

            html.Div(className='col-4', children=[
                html.Label(htmlFor='bank-id', children=['Bank']),
                dcc.Dropdown(
                    id='account-importer-dropdown',
                    options=[{'label': i['label'], 'value': i['value']} for i in accout_importers],
                    # options=accout_importers,
                    # value=accout_importers,
                    clearable=False
                ),
                html.Div(id='hidden-div', style={'display': 'none'}),
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
        ]),
        html.Div(id='upload-status-container', hidden=True, children=[
            dcc.Input(id='upload-status', type='hidden', value="no-info")
        ])
    ])


def __account_tab(account_data, account_name):

    return dcc.Tab(label=account_name, selected_className='accounts-tab-selected', children=[

        html.Div(className='row', children=[
            dcc.Graph(figure=__account_chart(account_data))
        ]),

        table.DataTable(
            id=account_name + '-table',
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
