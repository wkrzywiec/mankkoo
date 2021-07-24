import dash_html_components as html
import dash_core_components as dcc
import scripts.main.total as total
import scripts.main.data as dt
import widget

data = dt.load_data()

total_money = total.total_money_data(data)
total_table = widget.total_money_table(total_money)
total_pie = widget.total_money_pie(total_money)

total_chart = widget.total_money_chart(data['total'])

def main_page():
    return html.Div(className='height-100 container main-body', children=[

        html.Div(className='row', children=[
            html.Div(className='col-3', children=[
                html.Div(className='card card-indicator', children=[
                     html.Div(className='card-body card-body-indicator', children=[
                        html.Span('My Wealth', className='card-body-title'),
                        html.Span('{:,.2f} PLN'.format(total_money['Total'].sum()).replace(',', ' '))
                     ])
                ])
            ])
        ]),

        html.Div(className='row', children=[
            html.Div(className='col-4', children=[
                html.Div(className='card card-indicator', style={'height': '366px', 'width': '400px'}, children=[
                    html.Div(className='card-body card-body-plotly', children=[
                        html.Span('Wealth Distribution', className='card-body-title', style={'margin-bottom': '40px'}),
                        total_table
                    ])     
                ])
            ]),
            html.Div(className="col-5", children=[
                html.Div(className='card card-indicator', children=[
                    html.Div(className='card-body card-body-plotly', children=[
                        html.Span('Wealth Distribution', className='card-body-title', style={'margin-bottom': '20px'}),
                        html.Div(dcc.Graph(figure=total_pie), style={'width': '400px'})
                    ])
                ])
            ])
        
        ]),

        html.Div(className='row', style={'padding-bottom': '50px'}, children=[
             html.Div(className='col-12', children=[
                html.Div(className='card card-indicator', children=[
                    html.Div(className='card-body card-body-plotly', children=[
                        html.Span('Wealth History', className='card-body-title'),
                        html.Div(dcc.Graph(figure=total_chart), style={'width': '1200px'})
                    ])
                    
                ])
            ]),
        ])
    ])
