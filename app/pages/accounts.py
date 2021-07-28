from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

def account_page():
    return html.Div(className='height-100 container main-body', children=[

        html.Div(className='row', children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False),
            html.Div(id='output-data-upload', style={'display': 'none'})
        ])
    ])
