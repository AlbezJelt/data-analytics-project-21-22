from copy import deepcopy
import dash
from dash import html, dcc, dash_table, callback, Input, Output, callback_context, State
import igraph as ig
import dash_bootstrap_components as dbc
import utils
import pandas as pd
from dash.exceptions import PreventUpdate

# Load data
g = ig.Graph.Read('./data/graphs/april2022_Lspace.graphml')

df = pd.DataFrame({attr: g.vs[attr] for attr in g.vertex_attributes()})

dash.register_page(__name__, name='Network properties')

main_container = html.Div(className='container-fluid page-container', children=[
    dbc.Container([
        dbc.Row(
        [
            dbc.Col(dcc.Graph(id='graph_prop', responsive=False)),
            dbc.Col(
                html.Div([
                    dbc.Row(dcc.Markdown("### Network's general properties")),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Number of nodes", className="card-title"),
                                dcc.Markdown(
                                    "Trenord network is composed of **428** nodes."
                                )
                            ]
                        ), color="light"
                    ),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Number of edges", className="card-title"),
                                dcc.Markdown(
                                    "Trenord network is composed of **1173** edges."
                                )
                            ]
                        ), color="light"
                    ),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Diameter", className="card-title"),
                                dcc.Markdown(
                                    "The biggest distance between stations in the network is **26**."
                                )
                            ]
                        ), color="light"
                    ),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Average shortest path", className="card-title"),
                                dcc.Markdown(
                                    "The average shortest path between nodes in the network is **9.52**."
                                )
                            ]
                        ), color="light"
                    ),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Average Degree", className="card-title"),
                                dcc.Markdown(
                                    "The average degree of the nodes is **5.48**."
                                )
                            ]
                        ), color="light"
                    ),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Assortativity degree", className="card-title"),
                                dcc.Markdown(
                                    "Trenord network tends to be an assortative network, with a degree of **0.23**."
                                )
                            ]
                        ), color="light"
                    ),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Average Clustering coefficient", className="card-title"),
                                dcc.Markdown(
                                    "The probability that two neighbors of a randomly selected node link to each other is **0.22**."
                                )
                            ]
                        ), color="light"
                    ),
                    ])
                #)
            )
        ]),
        html.P("Find the shortest path", className="lead"),
        dcc.Dropdown(g.vs['label'], placeholder="Select a station", id='drop1'),
        dcc.Dropdown(g.vs['label'], placeholder="Select a station", id='drop2'),
        dbc.Button(id='submit-button', n_clicks=0, children='Submit', outline=True, color="success", className="me-1"),
        html.Div(id='output-state'),
        html.Hr(),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i, "hideable":False} for i in df.columns if i != 'name' and i != 'id'],
            data=df.to_dict('records'),
            page_size=25,
            fixed_rows={'headers': True},
            fixed_columns={'headers': True, 'data': 1},
            style_table={'height': 'auto', 'overflowY': 'auto', 'overflowX': 'auto', 'minWidth': '100%'},
            style_cell={'height': 'auto','textAlign': 'center', 'minWidth': '180px', 'width': '180px', 'maxWidth': '180px'},
            style_as_list_view=True,
            sort_action='native',
            filter_action='native',
            row_selectable='multi',
            page_action='native',
            ###
            editable=False,
            sort_mode='multi',
            row_deletable=False,
            selected_rows=[],
            page_current= 0
        )
    ])
])

layout = html.Div(children=[
    html.H1(children='Network properties'),
    main_container
])


@callback(
    Output(component_id='graph_prop', component_property='figure'),
    Input('table', 'derived_virtual_row_ids'),
    Input('table', 'selected_row_ids'),
    Input('graph_prop', 'clickData'),
    Input('submit-button', 'n_clicks'),
    State('drop1', 'value'),
    State('drop2', 'value')
)
def on_table_change(row_ids, selected_row_ids, clickData, n_clicks, drop1, drop2):
    new_g = deepcopy(g)
    triggered_id = callback_context.triggered[0]['prop_id']
    vertex_size = []
    colors = None
    paths = None
    print("triggered_id", triggered_id)
    if triggered_id == "table.selected_row_ids": 
        selected_id_set = set(selected_row_ids or [])
        if row_ids is None:
            dff = df
            row_ids = dff
        colors = [
            '#F92104' if v['id'] in selected_id_set
            else '#6959CD'
            for v in new_g.vs
        ]
        vertex_size = [1.5 if v['id'] in selected_id_set else .5 for v in new_g.vs]   
    elif triggered_id == 'graph_prop.clickData': # Show neighbors
        colors = list()
        station = clickData['points'][0]['text']
        station_id = clickData['points'][0]['pointNumber']
        vicini = ['n' + str(g) for g in new_g.neighborhood(station_id, 1)]
        for v in new_g.vs:
            if v['label'] == station: 
                colors.append('#CC3BB8')
            elif v['id'] in vicini: 
                colors.append('#C08EF2')
            else: colors.append('#6959CD')
        vertex_size = [1.5 if v['label'] == station or v['id'] in vicini else .5 for v in new_g.vs]
    elif triggered_id == 'submit-button.n_clicks':  # Show shortest-path
        if drop1 is not None and drop2 is not None:
            try:
                node1 = new_g.vs.select(label=drop1)[0]['id']
                node2 = new_g.vs.select(label=drop2)[0]['id']
                vertex_path = new_g.vs[new_g.get_shortest_paths(v=int(node1.replace('n', '')), to=int(node2.replace('n', '')), output='vpath')[0]]
                indices = ['n' + str(i) for i in vertex_path.indices]
                colors = [
                    '#57E234' if v['id'] in indices
                    else '#6959CD'
                    for v in new_g.vs
                ]
                vertex_size = [2 if v['id'] in indices else .5 for v in new_g.vs]
                paths = []
                for v in new_g.vs:
                    elem = "Inf"
                    for i in enumerate(vertex_path.indices):
                        if v['id'] == 'n' + str(i[1]):
                            elem = str(i[0])
                    paths.append(elem)
            except Exception as e:
                print(e)
                raise PreventUpdate
    else:
        vertex_size = [.5 for _ in new_g.vs]

    new_g.vs['vertex_size'] = vertex_size
    fig = utils.graph_figure(new_g, colors, paths)
    fig.update_layout(transition_duration=500)
    return fig


@callback(
    Output('output-state', 'children'),
    Input('submit-button', 'n_clicks'),
    State('drop1', 'value'),
    State('drop2', 'value')
)
def update_output(n_clicks, drop1, drop2):
    if drop1 is not None and drop2 is not None and drop1 != drop2:
        new_g = deepcopy(g)
        try:
            node1 = new_g.vs.select(label=drop1)[0]['id']
            node2 = new_g.vs.select(label=drop2)[0]['id']
            vertex_path = new_g.vs[new_g.get_shortest_paths(v=int(node1.replace('n', '')), to=int(node2.replace('n', '')), output='vpath')[0]]
            return 'The shortest path connects: {}\n\nLenght: {}'.format([new_g.vs['label'][i] for i in vertex_path.indices], len(vertex_path.indices))
        except Exception as e:
            print(e)
            raise PreventUpdate