import dash_html_components as html
from scripts.main.base_logger import log

def stock_page():
    log.info('Loading stocks page')

    return html.Div([
        html.H3('You are on stocks page')
    ])
