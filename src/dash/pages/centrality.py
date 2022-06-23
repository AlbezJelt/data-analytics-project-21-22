import itertools
import pickle
from collections import defaultdict
from copy import deepcopy

import chart_studio.plotly as py
import plotly.express as ex
import plotly.figure_factory as ff

import dash
import dash_bootstrap_components as dbc
from fsspec import Callback
import igraph as ig
import numpy as np
from sqlalchemy import column
import utils
from dash import Dash, Input, Output, callback_context, dcc, html, callback
from plotly.graph_objs import *
from sklearn.preprocessing import minmax_scale, StandardScaler
import pandas as pd

# Load data
g = ig.Graph.Read('./data/graphs/april2022_Lspace.graphml')

dash.register_page(__name__)

with open('./data/plots/april2022_Lspace_robustness.pickle', 'rb') as f:
    robustness_data = pickle.load(f)

centrality_measures = {
    'degree': lambda x: x.degree(),
    'betweennes': lambda x: x.betweenness(directed = True),
    'closeness': lambda x: x.betweenness(),
    'pagerank': lambda x: x.closeness(),
    'strength_num_train': lambda x: x.pagerank(),
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
            dbc.Row(centrality_col),
            dbc.Row(dcc.Graph(id='robustness', figure=utils.robustness_figure(robustness_data))),
        ]
    )

@callback(
    Output(component_id='trenord-graph', component_property='figure'),
    Input(component_id='centrality_measures_dropdown', component_property='value'),
    Input('robustness', 'clickData')
)
def centrality_measures_dropdown_value_change(dropDown_value, clickData) -> Figure:
    new_g = deepcopy(g)
    centrality_measure = centrality_measures[dropDown_value]
    triggered_id = callback_context.triggered[0]['prop_id']
    vertex_size = []
    if 'robustness.clickData' == triggered_id:
        centrality_measure_name = list(centrality_measures.keys())[clickData['points'][0]['curveNumber']]
        rem_perc = clickData['points'][0]['x']
        removed_labels = robustness_data.loc[(robustness_data['rem_perc'] <= rem_perc) & (robustness_data['centrality_measure'] == centrality_measure_name), ['removed']].to_numpy()
        removed_labels = np.hstack(np.ravel(removed_labels))
        removed_ids = [v.index for v in g.vs if v['name'] in removed_labels]
        tmp_g = deepcopy(g)
        tmp_g.delete_vertices(removed_ids)
        cent = defaultdict(lambda: 0.0, zip(tmp_g.vs['name'], minmax_scale(centrality_measure(tmp_g))))
        vertex_size = [cent[v['name']] for v in g.vs]

    else:
        vertex_size = minmax_scale(centrality_measure(g))

    new_g.vs['vertex_size'] = vertex_size
    fig = utils.graph_figure(new_g)
    fig.update_layout(transition_duration=500)
    return fig

@callback(
    Output('top-15', 'figure'),
    Input('centrality_measures_dropdown', 'value')
)
def top_15_by_centrality(dropDown_value) -> Figure:
    #centrality = StandardScaler().fit_transform(np.array(centrality_measures[dropDown_value](g)).reshape(-1,1)).T.ravel()
    centrality = np.array(centrality_measures[dropDown_value](g))
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
def top_15_by_centrality(dropDown_value) -> Figure:
    #centrality = StandardScaler().fit_transform(np.array(centrality_measures[dropDown_value](g)).reshape(-1,1)).T.ravel()
    centrality = np.array(centrality_measures[dropDown_value](g))
    fig = ff.create_distplot([centrality], [dropDown_value])
    fig.update_layout(title_text=f'{dropDown_value} distribution')
    return fig