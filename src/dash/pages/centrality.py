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
        dbc.Row(dcc.Dropdown(list(centrality_measures.keys()), list(centrality_measures.keys())[0], id='centrality_measures_dropdown')),
        dbc.Col(dcc.Graph(id='top-15', responsive=True)),
        dbc.Col(dcc.Graph(id='density', responsive=True))
    ]

    return html.Div(
        className='container-fluid page-container',
        children=[
            html.H1(children='Centrality analysis'),
            dbc.Row(dcc.Graph(id='trenord-graph')),
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

@callback(
    Output('density', 'figure'),
    Input('centrality_measures_dropdown', 'value')
)
def centrality_distplot(dropDown_value) -> Figure:
    centrality = np.array(g.vs[dropDown_value])
    fig = ff.create_distplot([centrality], [dropDown_value], bin_size=.1, histnorm='probability')
    fig.data[1].y = minmax_scale(fig.data[1].y) / centrality.shape[0]
    fig.update_layout(title_text=f'{dropDown_value} distribution')
    return fig