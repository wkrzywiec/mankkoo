import dash_html_components as html
from scripts.main.base_logger import log


def debt_page():
    log.info("Loading debt page")

    return html.Div([
        html.H3('You are on debt page')
    ])