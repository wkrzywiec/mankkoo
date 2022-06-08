import dash_html_components as html
from scripts.main.base_logger import log

def settings_page():
    log.info('Loading settings page')

    return html.Div([
        html.H3('You are on Settings page')
    ])
