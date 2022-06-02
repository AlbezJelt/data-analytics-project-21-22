import igraph as ig
import chart_studio.plotly as py
import utils
from dash import Dash, dcc, html
from plotly.graph_objs import *

g = ig.Graph.Read('../../data/graphs/april2022.graphml')
layout = utils.layout_geo(g)
labels = list(g.vs['label'])
N = len(labels)
E = [e.tuple for e in G.es]  # list of edges

app = Dash(__name__)

Xn=[layt[k][0] for k in range(N)]
Yn=[layt[k][1] for k in range(N)]
Xe=[]
Ye=[]
for e in E:
    Xe+=[layt[e[0]][0],layt[e[1]][0], None]
    Ye+=[layt[e[0]][1],layt[e[1]][1], None]

trace1=Scatter(x=Xe,
               y=Ye,
               mode='lines',
               line= dict(color='rgb(210,210,210)', width=1),
               hoverinfo='none'
               )
trace2=Scatter(x=Xn,
               y=Yn,
               mode='markers',
               name='ntw',
               marker=dict(symbol='circle-dot',
                                        size=5,
                                        color='#6959CD',
                                        line=dict(color='rgb(50,50,50)', width=0.5)
                                        ),
               text=labels,
               hoverinfo='text'
               )

axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
          zeroline=False,
          showgrid=False,
          showticklabels=False,
          title=''
          )

width=800
height=800
layout=Layout(title= "Trenord public transportation network",
    font= dict(size=12),
    showlegend=False,
    autosize=False,
    width=width,
    height=height,
    xaxis=layout.XAxis(axis),
    yaxis=layout.YAxis(axis),
    margin=layout.Margin(
        l=40,
        r=40,
        b=85,
        t=100,
    ),
    hovermode='closest',
    )

data=[trace1, trace2]
fig=Figure(data=data, layout=layout)

app.layout = html.Div(children=[
    html.H1(children='Trenord public transportation network'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
