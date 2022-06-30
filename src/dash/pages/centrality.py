import pickle
from collections import defaultdict
from copy import deepcopy

import plotly.express as ex
import plotly.figure_factory as ff

import dash
import dash_bootstrap_components as dbc
import igraph as ig
import numpy as np
import utils
from dash import  Input, Output, callback_context, dcc, html, callback
from plotly.graph_objs import *
from sklearn.preprocessing import minmax_scale
import pandas as pd
from scipy.stats import gaussian_kde

# Load data
g = ig.Graph.Read('./data/graphs/april2022_Lspace.graphml')

dash.register_page(__name__)

with open('./data/plots/april2022_Lspace_robustness.pickle', 'rb') as f:
    robustness_data = pickle.load(f)

centrality_measures = {
    'degree': lambda x: x.degree(),
    'betweennes': lambda x: x.betweenness(directed=True),
    'closeness': lambda x: x.closeness(),
    'pagerank': lambda x: x.pagerank(),
    'strength_num_train': lambda x: x.strength(weights='num_train'),
    'pagerank_num_train': lambda x: x.pagerank(weights='num_train')
}

def layout():

    centrality_col = [
        dbc.Col(dcc.Graph(id='density', figure=centrality_distplot(), responsive=True))
    ]

    graph_col = [
        dbc.Col(dcc.Graph(id='trenord-graph')),
        dbc.Col([
            dbc.Row(dcc.Dropdown(list(centrality_measures.keys()), list(centrality_measures.keys())[0], id='centrality_measures_dropdown')),
            dbc.Row(dcc.Graph(id='top-15', responsive=True, style={'padding-top': '20px'}))
        ])
    ]

    return html.Div(
        className='container-fluid page-container',
        children=[
            html.H1(children='Centrality analysis'),
            dbc.Row(graph_col),
            dbc.Row(centrality_col)
        ]
    )

@callback(
    Output('trenord-graph', 'figure'),
    Input('centrality_measures_dropdown', 'value')
)
def centrality_measures_dropdown_value_change(dropDown_value) -> Figure:
    new_g = deepcopy(g)
    vertex_size = minmax_scale(g.vs[dropDown_value])
    new_g.vs['vertex_size'] = vertex_size
    fig = utils.graph_figure(new_g)
    fig.update_layout(transition_duration=500)
    return fig

@callback(
    Output('top-15', 'figure'),
    Input('centrality_measures_dropdown', 'value')
)
def top_15_by_centrality(dropDown_value) -> Figure:
    centrality = np.array(g.vs[dropDown_value])
    centrality_indexes = utils.top_n_indices(centrality, 15)
    centrality_data = (centrality[i] for i in centrality_indexes)
    centrality_label = (g.vs[i]['label'] for i in centrality_indexes)
    df = pd.DataFrame(
        list(zip(centrality_label, centrality_data)),
        columns=['station', dropDown_value]
    )
    fig = ex.bar(df, x='station', y=dropDown_value, title=f'Top 15 station by {dropDown_value} centrality')
    return fig

def centrality_distplot() -> Figure:   
    # centralities = pd.DataFrame(
    #     ((measure, value) for measure in centrality_measures.keys() for value in g.vs[measure]),
    #     columns=['centrality', 'value']
    # )
    #fig = ex.histogram(centralities, x="value", color="centrality", histnorm='probability')
    fig = fig = ff.create_distplot(
        [g.vs[measure] for measure in centrality_measures.keys()], 
        list(centrality_measures.keys()),
        rug_text=[g.vs['label'] for measure in centrality_measures.keys()], 
        bin_size=.01, 
        histnorm='probability')
    fig.update_layout(title_text=f'Centrality distributions')
    return fig