import itertools as it

import igraph as ig
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
from plotly.graph_objs import *


def layout_geo(g: ig.Graph) -> ig.Layout:
    return ig.Layout(it.zip_longest(g.vs['lat'], g.vs['lon']))


def top_n_indices(arr: np.ndarray, n: int, sort: bool = True) -> np.ndarray:
    top_n = np.argpartition(arr, -n)[-n:]
    if sort:
        return top_n[np.argsort(arr[top_n])[::-1][:n]]
    else:
        return top_n


def robustness_figure(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    fig = px.line(df, x="rem_perc", y="S", color="centrality_measure", line_dash="centrality_measure")
    fig.update_xaxes(
        range=[0,100],  # sets the range of xaxis
        constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
    )
    fig.update_yaxes(
        scaleanchor = "x",
        scaleratio = 1,
    )
    return fig


def graph_figure(g: ig.Graph, color=None) -> plotly.graph_objs.Figure:
    ly = layout_geo(g)
    labels = list(g.vs['label'])
    N = len(labels)
    E = [e.tuple for e in g.es]  # list of edges

    markers = {
        'Xn': [ly[k][0] for k in range(N)],
        'Yn': [ly[k][1] for k in range(N)],
        'vertex_size': np.array(g.vs['vertex_size'])
    }

    Xe = []
    Ye = []
    for e in E:
        Xe += [ly[e[0]][0], ly[e[1]][0], None]
        Ye += [ly[e[0]][1], ly[e[1]][1], None]

    trace1 = Scatter(x=Xe,
                     y=Ye,
                     mode='lines',
                     line=dict(color='rgb(210,210,210)', width=1),
                     hoverinfo='none'
                     )
    trace2 = Scatter(x=markers['Xn'],
                     y=markers['Yn'],
                     mode='markers',
                     name='ntw',
                     marker=dict(symbol='circle-dot',
                                 color='#6959CD' if color is None else color,
                                 line=dict(color='rgb(50,50,50)', width=0.5)
                                 ),
                     marker_size=(markers['vertex_size'] + 0) * 10,
                     text=labels,
                     hoverinfo='text'
                     )

    axis = dict(showline=False,  # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )
    
    width = 800
    height = 800
    layout = plotly.graph_objs.Layout(
                    font=dict(size=12),
                    showlegend=False,
                    autosize=True,
                    width=width,
                    height=height,
                    xaxis=plotly.graph_objs.layout.XAxis(axis),
                    yaxis=plotly.graph_objs.layout.YAxis(axis),
                    hovermode='closest',
                    )

    data = [trace1, trace2]
    return Figure(data=data, layout=layout)
