import dash_html_components as html
import dash_core_components as dcc
import dash_table as table
import pandas as pd

from scripts.main.base_logger import log
import scripts.main.config as config


def settings_page():
    log.info('Loading settings page')

    user_config = config.load_user_config()

    bank_accounts = pd.DataFrame(user_config['accounts']['definitions'])
    default_importer = user_config['accounts']['ui']['default_importer']

    return html.Div(className='height-100 container main-body', children=[
        html.H1('Settings', className='title'),
        
        html.H3('Bank accounts', className='title subtitle'),
        table.DataTable(
            id='bank-accounts-table',
            editable=True,
            row_deletable=True,
            columns=[{"name": i, "id": i} for i in bank_accounts.columns],
            data=bank_accounts.to_dict('records'),
            page_size=10,
            style_cell={
                'textAlign': 'left',
                'font-family': 'Rubik'},
            style_header={
                'backgroundColor': 'rgba(245, 214, 186, 0.7)',
                'font-family': 'Rubik',
                'fontWeight': 'bold'}),
        html.Div(id='account-settings-change-container', hidden=True, children=[
            dcc.Input(id='account-settings-change', type='hidden', value="no-info")
        ]),


        html.Button('Add Bank Account', id='add-account-button', n_clicks=0),
        html.H3('Default bank account importer', className='title subtitle'),
        html.P(default_importer),
        html.H3('Hide bank accounts', className='title subtitle')
    ])
