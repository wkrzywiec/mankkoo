import dash_html_components as html

def navbar(pathname: str):

    navbar = html.Div(className='l-navbar', id='nav-bar', children=[
            html.Nav(className='nav', children=[
                html.Div(children=[
                    html.A(href='/', className='nav_logo', children=[
                        html.I(className='bx bx-layer nav_logo-icon'),
                        html.Span('mankkoo', className='nav_logo-name')
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/', className='nav_link', children=[
                            html.I(className='bx bx-grid-alt nav_icon'),
                            html.Span('Overview', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/accounts', className='nav_link', children=[
                            html.I(className='bx bx-euro nav_icon'),
                            html.Span('Accounts', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/investments', className='nav_link', children=[
                            html.I(className='bx bx-briefcase nav_icon'),
                            html.Span('Investments', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/stocks', className='nav_link', children=[
                            html.I(className='bx bx-bar-chart nav_icon'),
                            html.Span('Stock', className='nav_name')
                        ])
                    ]),
                    html.Div(className='nav_list', children=[
                        html.A(href='/retirement', className='nav_link', children=[
                            html.I(className='bx bx-medal nav_icon'),
                            html.Span('Retirement', className='nav_name')
                        ])
                    ])
                ])
            ])
    ])

    for nav in navbar.children[0].children[0].children:
        if nav.className == 'nav_list':
            if nav.children[0].href == pathname:
                nav.children[0].className = 'nav_link active'

    return navbar
