import dash
from dash import html, dcc
import utils
import igraph as ig
import dash_bootstrap_components as dbc
import pickle

dash.register_page(__name__)

with open('./data/plots/april2022_Lspace_robustness.pickle', 'rb') as f:
    robustness = pickle.load(f)

with open('./data/plots/april2022_Lspace_average_path_length_robustness.pickle', 'rb') as f:
    l_robustness = pickle.load(f)

def layout(): 
    return html.Div(
        className='container-fluid page-container',
        children=[
            html.H1(children='Vulnerabilities'),
            dcc.Graph(
                id='robustness_figure', 
                figure=utils.robustness_figure(robustness), 
                responsive=True
            ),
            dcc.Graph(
                id='average_path_length_robustness_figure', 
                figure=utils.average_path_length_robustness_figure(l_robustness), 
                responsive=True
            )
    ])