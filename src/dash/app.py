from turtle import st
import dash_bootstrap_components as dbc
import utils

from dash import Dash, Input, Output, State, dcc, html, dcc
import dash

app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    use_pages=True
)

sidebar = html.Div(
    [
        html.H2("Trenord", className="display-4"),       
        html.P("Transportation network analysis", className="lead"),
        html.Hr(),
        dbc.Nav(
            [dbc.NavLink(page['name'], href=page['path'], active="exact") for page in dash.page_registry.values()],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    className="p-3 text-white bg-dark"
)

app.layout = html.Div(
    children=[
        sidebar,
        dash.page_container
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
