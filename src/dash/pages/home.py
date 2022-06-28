import dash
from dash import html, dcc
import utils
import igraph as ig
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

g = ig.Graph.Read('./data/graphs/april2022_Lspace.graphml')

layout = html.Div(
    className='container-fluid page-container',
    children=[
        html.H1(children='This is our Home page'),
        dcc.Graph(id='graph', figure=utils.mapbox(g), responsive=True)

])