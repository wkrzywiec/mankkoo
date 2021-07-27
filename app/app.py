import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import scripts.main.config as config
import scripts.main.models as models
import scripts.main.data as dt
from scripts.main.base_logger import log
import navbar
import pages.main as main
import pages.accounts as pa
import pages.investments as pi
import pages.stocks as ps
import pages.retirement as pr

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/boxicons@latest/css/boxicons.min.css'
]

external_scripts = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js'
]

mankkoo_colors = ['#A40E4C', '#ACC3A6', '#F5D6BA', '#F49D6E', '#27474E', '#BEB8EB', '#6BBF59', '#C2E812', '#5299D3']

log.info("Starting mankkoo's server")

app = dash.Dash(__name__,
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts)
app.config.suppress_callback_exceptions = True

config.init_data_folder()

app.layout = html.Div(children=[
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
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

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        dt.add_new_operations(models.Bank.PL_MILLENIUM, list_of_names, '360')

if __name__ == '__main__':
    app.run_server(debug=True)
