import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import navbar
import pages.main as main
import pages.accounts as pa
import pages.investments as pi
import pages.stocks as ps
import pages.retirement as pr

import scripts.main.config as config
import scripts.main.models as models
import scripts.main.data as dt
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
    elif pathname == '/stocks':
        page = ps.stock_page()
    elif pathname == '/retirement':
        page = pr.retirement_page()
    else:
        page = main.main_page()

    return html.Div(children=[navbar.navbar(app, pathname), page])

@app.callback(Output('upload-status', 'value'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              State('bank-id', 'value'),
              State('account-name', 'value'),
              State('account-type', 'value')
)
def update_output(list_of_contents, list_of_names, list_of_dates, bank_id, account_name, account_type):
    if list_of_contents is not None:
        try:
            dt.add_new_operations(models.Bank[bank_id], account_name, contents=list_of_contents)
            return 'success'
        except Exception as ex:
            log.info(f'Error occured: {ex}')
            return 'failure'


if __name__ == '__main__':
    log.info("Starting mankkoo's server")
    app.run_server(debug=True)
