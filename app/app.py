import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import navbar
import pages.main as main
import pages.accounts as pa
import pages.investments as pi
import pages.debt as pd
import pages.stocks as ps
import pages.retirement as pr
import pages.settings as pset

import scripts.main.config as config
import scripts.main.models as models
import scripts.main.account as account
from scripts.main.base_logger import log

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/boxicons@latest/css/boxicons.min.css',
    'https://cdn.jsdelivr.net/npm/sweetalert2@11.1.7/dist/sweetalert2.min.css'
]

external_scripts = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/sweetalert2@11.1.7/dist/sweetalert2.min.js',
]

mankkoo_colors = ['#A40E4C', '#ACC3A6', '#F5D6BA', '#F49D6E', '#27474E', '#BEB8EB', '#6BBF59', '#C2E812', '#5299D3']

app = dash.Dash(__name__,
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts)
app.config.suppress_callback_exceptions = True
app.title = 'Mankkoo - Personal finance dashboard'

config.init_data_folder()

app.layout = html.Div(children=[
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname')
)
def display_page(pathname):

    if pathname == '/accounts':
        page = pa.account_page()
    elif pathname == '/investments':
        page = pi.inv_page()
    elif pathname == '/debt':
        page = pd.debt_page()
    elif pathname == '/stocks':
        page = ps.stock_page()
    elif pathname == '/retirement':
        page = pr.retirement_page()
    elif pathname == '/settings':
        page = pset.settings_page()
    else:
        page = main.main_page()

    return html.Div(children=[navbar.navbar(app, pathname), page])

# account.py
@app.callback(Output('upload-status', 'value'),
              Input('upload-data', 'contents'),
              Input('account-importer-dropdown', 'value')
)
def update_output(list_of_contents, account_id):
    if list_of_contents is not None:
        try:

            account.add_new_operations(account_id, contents=list_of_contents)
            return 'success'
        except Exception as ex:
            log.info(f'Error occured: {ex}')
            return 'failure'

# settings.py
@app.callback(
    Output('bank-accounts-table', 'data'),
    Input('add-account-button', 'n_clicks'),
    State('bank-accounts-table', 'data'),
    State('bank-accounts-table', 'columns'))
def account_settings_add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output('account-settings-change', 'value'),
    [Input('bank-accounts-table', 'data_previous')],
    [State('bank-accounts-table', 'data')])
def account_settings_remove_rows(previous, current):

    if previous is None:
        return 'success'
    else:
        
        if (len(current) < len(previous)):
            log.info('Account config entry removed')
            __update_accounts_config(current)
            return 'success'
        
        pairs = zip(current, previous)
        if any(x != y for x, y in pairs):
            log.info('Account config entry was modified')
            __update_accounts_config(current)
        else:
            log.info('None of account config entry was modified')
        return 'success'


def __update_accounts_config(current):
    user_config = config.load_user_config()
    user_config['accounts']['definitions'] = current
    config.save_user_config(user_config)


if __name__ == '__main__':
    log.info("Starting mankkoo's server")
    app.run_server(debug=True)
