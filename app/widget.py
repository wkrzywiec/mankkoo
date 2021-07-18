from dash_table.Format import Format, Group, Scheme, Symbol
from dash_table import DataTable, FormatTemplate
import plotly.express as px


def total_money_table(data):
    table = DataTable(
        id='total_money_table',
        columns=[
            dict(id='Type', name='Type'),
            dict(id='Total', name='Total', type='numeric', format=Format(
                    scheme=Scheme.fixed,
                    precision=2,
                    group=Group.yes,
                    groups=3,
                    group_delimiter=' ',
                    decimal_delimiter=',',
                    symbol=Symbol.no)
                    ),
            dict(id='Percentage', name='Percentage', type='numeric', format=FormatTemplate.percentage(2))
        ],
        data=data.to_dict('records'),
        style_cell={
            'textAlign': 'right',
            'height': 'auto',
            # all three widths are needed
            'minWidth': '120px', 'width': '120px', 'maxWidth': '120px',
            'whiteSpace': 'normal'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'Type'},
                'textAlign': 'left'
            },
            
        ],
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{{Total}} = {}'.format(data['Total'].sum())
                },
                'color': 'tomato',
                'textDecoration': 'underline',
                'fontWeight': 'bold'
            }
        ],
        style_as_list_view=True,
        fill_width=False
    )
    return table

def total_money_pie(data):
    data = data.drop(columns=['Percentage'])
    pie = px.pie(data, values='Total', names='Type', title='Total Money distribution')
    pie.update_traces(textposition='inside', textinfo='percent+label')
    return pie

def total_money_chart(data):
    chart = px.line(data, x='Date', y='Total', title='Total money')
    return chart
