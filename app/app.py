import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import widget
import scripts.main.config as config

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
app = dash.Dash(__name__,
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts)

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

    return html.Div(children=[widget.navbar(pathname), page])

if __name__ == '__main__':
    app.run_server(debug=True)
