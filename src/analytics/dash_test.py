import chart_studio.plotly as py
import igraph as ig
import utils
from dash import Dash, dcc, html, Input, Output
from plotly.graph_objs import *
import pickle
from copy import deepcopy
from sklearn.preprocessing import minmax_scale

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

app = Dash(__name__)

app.layout = html.Div(class='container', children=[
    html.H1(children='Trenord public transportation network'),

    html.Div(children=[
        dcc.Dropdown(list(centrality_measures.keys()), list(centrality_measures.keys())[0], id='centrality_measures_dropdown'),
        html.Div(children=[
            dcc.Graph(id='example-graph'),
            dcc.Graph(
                id='robustness',
                figure=utils.robustness_figure(robustness_data)
            )
        ])
    ]),


])


@app.callback(
    Output(component_id='example-graph', component_property='figure'),
    Input(component_id='centrality_measures_dropdown', component_property='value')
)
def centrality_measures_dropdown_value_change(value) -> Figure:
    new_g = deepcopy(g)
    new_g.vs['vertex_size'] = minmax_scale(centrality_measures[value](new_g))
    fig = utils.graph_figure(new_g)
    fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
