import chart_studio.plotly as py
import igraph as ig
import utils
from dash import Dash, dcc, html, Input, Output, callback_context
from plotly.graph_objs import *
import pickle
from copy import deepcopy
from sklearn.preprocessing import minmax_scale
import dash_bootstrap_components as dbc
import numpy as np
from collections import defaultdict
import itertools

# Load data
g = ig.Graph.Read('./data/graphs/april2022_Lspace.graphml')
with open('./data/plots/april2022_Lspace_robustness.pickle', 'rb') as f:
    robustness_data = pickle.load(f)
centrality_measures = {
    'degree': lambda x: x.degree(),
    'betweennes': lambda x: x.strength(weights='num_train'),
    'closeness': lambda x: x.betweenness(),
    'pagerank': lambda x: x.closeness(),
    'strength_num_train': lambda x: x.pagerank(),
    'pagerank_num_train': lambda x: x.pagerank(weights='num_train')
}

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H1(children='Trenord public transportation network'),
    dbc.Row(dbc.Col(dcc.Dropdown(list(centrality_measures.keys()), list(centrality_measures.keys())[0], id='centrality_measures_dropdown'))),
    dbc.Row([
            dbc.Col(dcc.Graph(id='example-graph')),
            dbc.Col(dcc.Graph(
                id='robustness',
                figure=utils.robustness_figure(robustness_data)
            ))
    ]),
])


@app.callback(
    Output(component_id='example-graph', component_property='figure'),
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



if __name__ == '__main__':
    app.run_server(debug=True)
