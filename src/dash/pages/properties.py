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
centrality_measures = {
    'degree': lambda x: x.degree(),
    'in-degree': lambda x: x.degree(mode="in-degree"),
    'out-degree': lambda x: x.degree(mode="out-degree"),
    'betweennes': lambda x: x.betweenness(directed=True),
    'closeness': lambda x: x.closeness(),
    'pagerank': lambda x: x.pagerank(directed=True),
    #'strength_num_train': lambda x: x.pagerank(),
    #'pagerank_num_train': lambda x: x.pagerank(weights='num_train')
}
for x in list(centrality_measures.keys()): df.insert(len(df.columns), x, centrality_measures[x](g))

dash.register_page(__name__, name='Network properties')

main_container = html.Div(className='container-fluid page-container', children=[
    dbc.Container([
        dcc.Graph(id='graph', responsive=False),
        html.P("Find the shortest path", className="lead"),
        dcc.Input(id='input-1', type='text', placeholder="Source name..."),
        dcc.Input(id='input-2', type='text', placeholder="Destination name..."),
        dbc.Button(id='submit-button', n_clicks=0, children='Submit', outline=True, color="success", className="me-1"),
        html.Div(id='output-state'),
        html.Hr(),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i, "hideable":False} for i in df.columns if i != 'name'],
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
            row_deletable=True,
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
    Output(component_id='graph', component_property='figure'),
    Input('table', 'derived_virtual_row_ids'),
    Input('table', 'selected_row_ids'),
    Input('graph', 'clickData'),
    #Input('table', 'data')
    Input('submit-button', 'n_clicks'),
    State('input-1', 'value'),
    State('input-2', 'value')
)
def on_table_change(row_ids, selected_row_ids, clickData, n_clicks, input1, input2):
    new_g = deepcopy(g)
    triggered_id = callback_context.triggered[0]['prop_id']
    vertex_size = []
    colors = None
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
    elif triggered_id == 'graph.clickData': # Show neighbors
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
        if input1 is not None and input2 is not None and input1 != input2:
            try:
                vertex_path = new_g.vs[new_g.get_shortest_paths(v=int(input1.replace('n', '')), to=int(input2.replace('n', '')), output='vpath')[0]]
                indices = ['n' + str(i) for i in vertex_path.indices]
                print('The shortest path connects {}'.
                    format([new_g.vs['label'][i] for i in vertex_path.indices]))
                colors = [
                    '#57E234' if v['id'] in indices
                    else '#6959CD'
                    for v in new_g.vs
                ]
                vertex_size = [2 if v['id'] in indices else .5 for v in new_g.vs]
            except Exception as e:
                print(e)
                raise PreventUpdate
    #elif triggered_id == 'table.data':
    #    set_df = set([i for i in data['name']])
    #    set_g = set(new_g.vs['name'])
    #    diff = set_g - set_df
    #    if len(diff) > 0:
    #        for elem in diff:
    #            new_g.delete_vertices(elem)
    #    vertex_size = [.5 for _ in new_g.vs]
    else:
        vertex_size = [.5 for _ in new_g.vs]

    new_g.vs['vertex_size'] = vertex_size
    fig = utils.graph_figure(new_g, colors)
    fig.update_layout(transition_duration=500)
    return fig

# TODO: Non riesco ad aggiornare la tabella quando rimuovo una entry, perchè all'eliminazione successiva, quello precedente ricompare...
        # penso sia dovuto al fatto che all'iterazione successiva il dataframe viene ricalcolato da 0
        # P.S. in teoria mi sarebbe piaciuto anche aggionare il grafo una volta eliminata l'entry...
#@callback(
#    Output('table', 'data'),
#    Input('table', 'data_previous'),
#    State('table', 'data')
#)
#def on_remove_update(previous, current):
#    new_g = deepcopy(g)
#    dff = df
#    if previous is not None:
#        print("hola")
#        s1 = set([i['name'] for i in current])
#        s2 = set([i['name'] for i in previous])
#        diff = s2 - s1
#        print('s2-s1: ', diff)
#        if len(diff) > 0:
#            for elem in diff:
#                print(elem)
#                new_g.delete_vertices(elem)
#                # TODO: da fare tramite callback
#                dff = dff[dff["name"].str.contains(str(elem)) == False]
#                for x in list(centrality_measures.keys()):
#                    del dff[x]
#                    dff.insert(len(dff.columns), x, centrality_measures[x](new_g))
#                #new_g.vs['vertex_size'] = [.5 for _ in new_g.vs]
#                #fig = utils.graph_figure(new_g)
#                #fig.update_layout(transition_duration=500)
#    return dff.to_dict('records')

@callback(
    Output('output-state', 'children'),
    Input('submit-button', 'n_clicks'),
    State('input-1', 'value'),
    State('input-2', 'value')
)
def update_output(n_clicks, input1, input2):
    new_g = deepcopy(g)
    if input1 is not None and input2 is not None and input1 != input2:
        try:
            vertex_path = new_g.vs[new_g.get_shortest_paths(v=int(input1.replace('n', '')), to=int(input2.replace('n', '')), output='vpath')[0]]
            print(vertex_path.indices)
            return 'The shortest path connects: {}'.format([new_g.vs['label'][i] for i in vertex_path.indices])
        except Exception as e:
            print(e)
            raise PreventUpdate