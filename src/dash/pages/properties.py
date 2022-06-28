from copy import deepcopy
import dash
from dash import html, dcc, dash_table, callback, Input, Output, callback_context, State
import igraph as ig
import dash_bootstrap_components as dbc
import utils, pickle
import pandas as pd
#import numpy as np
#from dash.exceptions import PreventUpdate

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

# for x in list(centrality_measures.keys()):
#     df.insert(len(df.columns), x, centrality_measures[x](g))

dash.register_page(__name__, name='Network properties')

main_container = html.Div(className='container-fluid page-container', children=[
    #dbc.Container(dcc.Graph(id='graph', responsive=False)),
    dbc.Container([
        #dbc.Alert(id='tbl_out'),
        #dbc.Button(
        #    "Analyze Network",
        #    color="info",
        #    outline=True,
        #    id="analyze",
        #    className="mb-3",
        #    disabled=False
        #),
        dcc.Graph(id='graph', responsive=False),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i, "hideable":False} for i in df.columns if i != 'id' and i != 'name'],
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


#@callback(
#    [Output(component_id='table', component_property='columns'),
#    Output(component_id='table', component_property='data'),
#    Output('analyze','disabled')],
#    Input(component_id='analyze', component_property='n_clicks'),
#    [State('table', 'derived_virtual_row_ids'),
#    State('table', 'columns'),
#    State('table', 'data')]
#)
#def displayClick(btn1, row_ids, columns, data):
#    print("callback_context.triggered][0]: ", callback_context.triggered[0]['prop_id'])
#    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
#    print("changed_id: ", changed_id)
#    #print("row_ids: ", row_ids)
#    if 'analyze.n_clicks' in changed_id:
#        if row_ids is None or columns is None:
#            raise PreventUpdate
#        print('Analyzing...')
#        print("existing_columns: ", columns)
#        existing_columns = any(c.get('id') in list(centrality_measures.keys()) for c in columns)
#        if existing_columns == True:
#            raise PreventUpdate
#        #for k in centrality_measures.keys():
#        #    print(k)
#        #    columns.append(
#        #        {
#        #            'name': k, 'id': k,
#        #        }
#        #    )
#        columns.append(
#            {
#                'id': '1', 'name': '1', 'renamable': True
#            }
#        )
#        columns.append(
#            {
#                'id': '2', 'name': '2', 'renamable': True
#            }
#        )
#        #data.append({c['id']: 'cacca' for c in columns})
#        print("existing_columns: ", columns)
#        return columns, data, True
#    else:
#        print('No buttons have been clicked yet')
#        return columns, data, False



@callback(
    Output(component_id='graph', component_property='figure'),
    Input('table', 'derived_virtual_row_ids'),
    Input('table', 'selected_row_ids')
)
def on_table_change(row_ids, selected_row_ids):
    new_g = deepcopy(g)
    triggered_id = callback_context.triggered[0]['prop_id']
    vertex_size = []
    colors = None
    print("triggered_id", triggered_id)
    if triggered_id == "table.selected_row_ids": 
        selected_id_set = set(selected_row_ids or [])
        if row_ids is None:
            dff = pd.DataFrame({attr: new_g.vs[attr] for attr in new_g.vertex_attributes()})
            row_ids = dff
        #'n352' in g.vs.find(label=station)['id']
        #g.vs.find(id=selected_row_ids)
        colors = [
            '#F92104' if v['id'] in selected_id_set
            else '#6959CD'
            for v in new_g.vs
        ]
        vertex_size = [1.5 if v['id'] in selected_id_set else .5 for v in new_g.vs]
    else:
        vertex_size = [.5 for v in new_g.vs]

    new_g.vs['vertex_size'] = vertex_size
    fig = utils.graph_figure(new_g, colors)
    fig.update_layout(transition_duration=500)
    return fig


#@callback(Output('tbl_out', 'children'), Input('table', 'active_cell'))
#def update_graphs(active_cell):
#    return str(active_cell) if active_cell else ""