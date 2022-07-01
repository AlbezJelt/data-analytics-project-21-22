import pickle
from collections import defaultdict
from copy import deepcopy

import dash
import dash_bootstrap_components as dbc
import igraph as ig
import numpy as np
import pandas as pd
import plotly.express as ex
import plotly.figure_factory as ff
from sympy import degree
import utils
from dash import Input, Output, callback, callback_context, dcc, html
from plotly.graph_objs import *
from scipy.stats import gaussian_kde
from sklearn.preprocessing import minmax_scale

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
        dcc.Markdown("""
            ### Centrality distribution

            Here we see how the different centralities are distributed within the network. Each bin corresponds to the probability that a station has of assuming a certain centrality value.
            For each bin, it is possible to check which station falls within the range of centrality values.
        """),
        dbc.Col(dcc.Graph(id='density', figure=centrality_distplot(), responsive=True))
    ]

    graph_col = [
        dbc.Col(dcc.Graph(id='trenord-graph')),
        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Markdown("**Select a centrality measure: **")),
                html.Div(                  
                    dcc.Dropdown(list(centrality_measures.keys()), list(centrality_measures.keys())[0], id='centrality_measures_dropdown'),
                    className='col-8'
                )
            ]),
            dcc.Markdown(id='measure-description'),
            dbc.Row(dcc.Graph(id='top-15', responsive=True,
                    style={'padding-top': '20px'}))
        ])
    ]

    return html.Div(
        className='container-fluid page-container',
        children=[
            dcc.Markdown("""
                # Centrality analysis

                Try to answer the following question:

                *"Which is/are the **most important station(s)** in the Trenord network?"*

                Of course, *"most important"* is not a truly quantifiable measure since importance depends on the actual meaning of the network. 
                What can be done is to **define measures** that consider different structural aspects of the network, each having a different meaning of centrality.

                Several measures of centrality are displayed in this section, and the top 15 stations are shown for each.
                In the network on the left, the size of the nodes reflects the selected measure.
            """),
            dbc.Row(graph_col),
            dbc.Row(centrality_col, style={'padding-top': '30px'})
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
    fig = ex.bar(df, x='station', y=dropDown_value,
                 title=f'Top 15 station by {dropDown_value} centrality, normalized between 0 and 1')
    return fig

@callback(
    Output('measure-description', 'children'),
    Input('centrality_measures_dropdown', 'value')
)
def centrality_measure_description(value):
    description = ""
    if value == 'degree':
        description = "The station **most connected to other stations** is the most important. Connections are considered both inbound (trains arriving) and outbound (trains departing)."   
    elif value == 'betweennes':
        description = "*\"How many trains must pass through a given station to reach the others in the least number of stops?\"*. The most important station is the one that **best serves as a broker** to reach the other."
    elif value == 'closeness':
        description = "Efficiency of one station in **propagating information** (trains) to all other stations. Based on the average shortest path between a node and all others."
    elif value == 'pagerank':
        description = "Each **directed edge corresponds to a *\"recommendation\"*** that the target node receives from the source node. The importance of a station is influenced by the importance of all other stations in its source neighborhood."
    elif value == 'strength_num_train':
        description = "Same meaning as degree measure but **connections are weighted** by number of passing trains. It denotes a portion of the network where there is a lot of train traffic."
    elif value == 'pagerank_num_train':
        description = "Same meaning as pagerank measure but **connections are weighted** by number of passing trains."

    return f"""
        **Measure description**

        {description}
    """

def centrality_distplot() -> Figure:
    fig = fig = ff.create_distplot(
        [g.vs[measure] for measure in centrality_measures.keys()],
        list(centrality_measures.keys()),
        rug_text=[g.vs['label'] for measure in centrality_measures.keys()],
        bin_size=.01,
        histnorm='probability')
    fig.update_layout(title_text=f'Centrality distributions')
    return fig
