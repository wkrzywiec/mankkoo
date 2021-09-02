from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as table

import scripts.main.importer.importer as importer
import scripts.main.models as models

def account_page():

    accounts = importer.load_data(models.FileType.ACCOUNT)
    millenium = accounts[accounts['Bank'] == 'Millenium']
    # millenium = millenium.drop(columns=['Bank', 'Type', 'Account', 'Category'])
    millenium = millenium[['Date', 'Title', 'Details', 'Operation', 'Balance', 'Currency', 'Comment']]
    millenium = millenium.iloc[::-1]

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
        ]),
        html.Div(className='row', children=[
            dcc.Tabs(
                id="tabs-styled-with-inline",
                children=[
                dcc.Tab(label='Millenium - 360',
                    selected_className='custom-tab-selected',
                    children=[
                        table.DataTable(
                            id='account-table',
                            columns=[{"name": i, "id": i} for i in millenium],
                            data=millenium.to_dict('records'),
                            page_size=20,
                            style_cell={
                                'textAlign': 'left',
                                'font-family': 'Rubik'
                            },
                            style_header={
                                'backgroundColor': 'rgba(245, 214, 186, 0.7)',
                                'font-family': 'Rubik',
                                'fontWeight': 'bold'
                            },
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{Operation} > 0',
                                        'column_id': 'Operation'
                                    },
                                    'backgroundColor': '#acc3a6'
                                },
                                {
                                    'if': {
                                        'filter_query': '{Operation} < 0',
                                        'column_id': 'Operation'
                                    },
                                    'backgroundColor': '#cc5a71',
                                    'color': 'white'
                                }
                            ])
                ]),
                dcc.Tab(
                    label='ING - Konto z Lwem Direct',
                    selected_className='custom-tab-selected',
                    children=[
                        html.Span('ING - Konto z Lwem Direct')
                ])
            ])
        ])
    ])
