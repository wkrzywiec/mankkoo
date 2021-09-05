import dash_html_components as html
from scripts.main.base_logger import log


def inv_page():
    log.info("Loading investments page")

    return html.Div([
        html.H3('You are on investments page')
    ])