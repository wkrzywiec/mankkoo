from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as table

import scripts.main.importer.importer as importer
import scripts.main.models as models

from scripts.main.base_logger import log

def account_page():
    log.info("Loading accounts page")

    accounts_data = importer.load_data(models.FileType.ACCOUNT)
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
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
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
            # Allow multiple files to be uploaded
            multiple=False),
            html.Div(id='output-data-upload', style={'display': 'none'})
        ]),
        html.Div(className='row', children=[
            dcc.Tabs(
                id="tabs-styled-with-inline",
                children=account_tabs)
        ])
    ])


def __account_tab(account_data, account_name):
    full_account_name = account_name[0] + ' - ' + account_name[1]

    return dcc.Tab(label=full_account_name, selected_className='custom-tab-selected', children=[
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
