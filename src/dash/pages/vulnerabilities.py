import dash
from dash import html, dcc, callback, Input, Output, callback_context
import utils
import igraph as ig
import pickle
import math
import numpy as np
import random
from copy import deepcopy


dash.register_page(__name__)

g = ig.Graph.Read('./data/graphs/april2022_Lspace.graphml')

centrality_measures = {
    'random_node': None,
    'degree': lambda x: x.degree(),
    'betweennes': lambda x: x.betweenness(directed=True),
    'closeness': lambda x: x.closeness(),
    'clustering': lambda x: x.transitivity_local_undirected(),
    'pagerank': lambda x: x.pagerank(directed=True),
    'strength_num_train': lambda x: x.strength(weights='num_train'),
    'pagerank_num_train': lambda x: x.pagerank(weights='num_train'),
    'merged': lambda x: list(utils.populate_rank(
        x,
        np.array([
            x.degree(), 
            x.strength(weights='num_train'), 
            x.betweenness(),
            x.closeness(),
            x.transitivity_local_undirected(),
            x.pagerank(weights='num_train')
        ])
    ))
}

with open('./data/plots/april2022_Lspace_robustness.pickle', 'rb') as f:
    robustness = pickle.load(f)

with open('./data/plots/april2022_Lspace_average_path_length_robustness.pickle', 'rb') as f:
    l_robustness = pickle.load(f)

def layout(): 
    return html.Div(
        className='container-fluid page-container',
        children=[
            dcc.Markdown("""
                # Network vulnerabilities

                This section shows how the network changes its structure by responding to different types of attacks, exploiting **percolation theory**. 
                Attacks are made by **removing nodes that are assigned to a certain measure of centrality**. 
                Iteratively one percent of the nodes that maximize that measure are removed, so it is recalculated. 
                The attack ends when there are no more nodes to remove or the measure cannot be further reduced.

                It has been observed in the literature that the behavior of a complex network under an attack that removes nodes or links 
                randomly can differ drastically from a scenario in which attacks are carried out according to certain criteria (measure).

                ### Trenord network graph
                Click anywhere on the charts below to see the effect of nodes removal on the graph.
            """),
            dcc.Graph(id='graph_v', responsive=False, style={'padding': '20px'}),
            dcc.Markdown("""
                ### Resilience of the giant component
            """),
            dcc.Graph(
                id='robustness_figure', 
                figure=utils.robustness_figure(robustness), 
                responsive=True,
                style={'padding': '20px'}
            ),
            dcc.Markdown("""
                The above graph shows the evolution of the giant component according to the centrality measures in the legend. 
                Also, the **random baseline removal method** is present.

                The size $\mathrm{S}$ of the giant component is calculated as: 

                $\mathrm{S} = \\frac{\mathrm{N}_{GCC}}{\mathrm{N}} \\times 100$

                where $\mathrm{N}_{GCC}$ represents the number of nodes within the giant component and $\mathrm{N}$ is the total number of nodes.

                ### Average shortest path variation
            """, mathjax=True),
            dcc.Graph(
                id='average_path_length_robustness_figure', 
                figure=utils.average_path_length_robustness_figure(l_robustness), 
                responsive=True,
                style={'padding': '20px'}
            ),
            dcc.Markdown("""
                Trend of the average shortest path versus the number of nodes removed for each measure. 
                The x-axis indicates the percentage of nodes removed, and the y-axis the value of the average shortest path.
            """, mathjax=True)
    ])


@callback(
    Output(component_id='graph_v', component_property='figure'),
    Input('robustness_figure', 'clickData'),
    Input('average_path_length_robustness_figure', 'clickData')
)
def on_table_change(clickData, clickData2):
    new_g = deepcopy(g)
    triggered_id = callback_context.triggered[0]['prop_id']
    vertex_size = []
    print("triggered_id", triggered_id)
    if triggered_id == "robustness_figure.clickData":
        id_measure = clickData['points'][0]['curveNumber']
        measure = list(centrality_measures.keys())[id_measure]
        to_remove = clickData['points'][0]['customdata'][0]

        ids_to_remove = [new_g.vs.select(label=r)[0]['name'] for r in to_remove]
        res = opercolation(new_g, centrality_measures[measure], ids_to_remove)
        new_g.delete_vertices(res)
        vertex_size = [.5 for _ in new_g.vs]
    elif triggered_id == "average_path_length_robustness_figure.clickData":
        id_measure = clickData2['points'][0]['curveNumber']
        measure = list(centrality_measures.keys())[id_measure]
        to_remove = clickData2['points'][0]['customdata'][0]

        ids_to_remove = [new_g.vs.select(label=r)[0]['name'] for r in to_remove]
        res = opercolation(new_g, centrality_measures[measure], ids_to_remove)
        new_g.delete_vertices(res)
        vertex_size = [.5 for _ in new_g.vs]
    else:
        vertex_size = [.5 for _ in new_g.vs]

    new_g.vs['vertex_size'] = vertex_size
    fig = utils.graph_figure(new_g)
    fig.update_layout(transition_duration=500)
    return fig


def opercolation(graph: ig.Graph, centrality_measure, list_to_compare):
    tmp_g = deepcopy(graph)  # Make a copy of the graph
    one_percent_size = int(math.ceil(len(tmp_g.vs) / 100))
    perc_removed = 0
    rem_vertex_name = []

    node_to_remove = []
    while len(tmp_g.vs) >= one_percent_size:
        perc_removed += 1
        # Calculate centrality measure
        if centrality_measure is not None:
            centrality = np.array(centrality_measure(tmp_g))
            max_centrality_vertex_ids = np.argpartition(
                centrality, -one_percent_size)[-one_percent_size:]
            # Extract original nodes ids
            rem_vertex_name = [v['name'] for v in tmp_g.vs.select(max_centrality_vertex_ids)]
            node_to_remove = node_to_remove + rem_vertex_name
            # Delete vertex with max centrality measure
            tmp_g.delete_vertices(max_centrality_vertex_ids)
        # Random node removal
        else:
            random.seed(42)
            ids = random.sample(tmp_g.vs['name'], one_percent_size)
            rem_vertex_name = ids
            tmp_g.delete_vertices(ids)
            node_to_remove = node_to_remove + ids
        
        if all([item in node_to_remove for item in list_to_compare]): break
    return node_to_remove