import dash_html_components as html
from scripts.main.base_logger import log

def retirement_page():
    log.info('Loading retirement page')

    return html.Div([
        html.H3('You are on retirement page')
    ])
