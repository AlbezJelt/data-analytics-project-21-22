import dash
import dash_cytoscape as cyto
import dash_html_components as html
import json


with open('./data/graphs/april2022_Lspace.cyjs') as f:
    graph = json.load(f)['elements']

for i, v in enumerate(graph['nodes']):
    graph['nodes'][i] = {
        **v,
        'position': {
            'x': v['data']['lat'] * 500,
            'y': v['data']['lon'] * 500
        }
    }


app = dash.Dash(__name__)

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape-two-nodes',
        style={'width': '2000px', 'height': '2000px'},
        layout={
            'name': 'preset',
            'idealEdgeLength': 100,
                'nodeOverlap': 20,
                'refresh': 20,
                'fit': True,
                'padding': 30,
                'randomize': False,
                'componentSpacing': 100,
                'nodeRepulsion': 400000,
                'edgeElasticity': 100,
                'nestingFactor': 5,
                'gravity': 80,
                'numIter': 1000,
                'initialTemp': 200,
                'coolingFactor': 0.95,
                'minTemp': 1.0
        },
        elements=graph,
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'width': 10, 
                    'height': 10
                }
            }
        ]
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)