import itertools as it
from statistics import mean

import igraph as ig
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
from plotly.graph_objs import *
import plotly.graph_objects as go


def layout_geo(g: ig.Graph) -> ig.Layout:
    return ig.Layout(it.zip_longest(g.vs['lat'], g.vs['lon']))

def top_n_indices(arr: np.ndarray, n: int, sort: bool = True) -> np.ndarray:
    top_n = np.argpartition(arr, -n)[-n:]
    if sort:
        return top_n[np.argsort(arr[top_n])[::-1][:n]]
    else:
        return top_n

def robustness_figure(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    fig = px.line(df, x="rem_perc", y="S", color="centrality_measure", line_dash="centrality_measure", hover_data=['removed'])
    return fig

def average_path_length_robustness_figure(df: pd.DataFrame) -> plotly.graph_objs.Figure:
    fig = px.line(df, x="rem_perc", y="average_path_length", color="centrality_measure", line_dash="centrality_measure", hover_data=['removed'])
    return fig

def graph_figure(g: ig.Graph, color=None, paths=None) -> plotly.graph_objs.Figure:
    ly = layout_geo(g)
    labels = list(g.vs['label'])
    N = len(labels)
    if paths is not None: labels = list(zip(labels, paths))
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

def mapbox(g: ig.Graph, color=None) -> plotly.graph_objs.Figure:
    ly = layout_geo(g)
    E = [e.tuple for e in g.es]  # list of edges

    def fXe(e): yield ly[e[0]][1]; yield ly[e[1]][1]; yield None
    def fYe(e): yield ly[e[0]][0]; yield ly[e[1]][0]; yield None
    Xe = list(it.chain.from_iterable(fXe(e) for e in E))
    Ye = list(it.chain.from_iterable(fYe(e) for e in E))

    fig = go.Figure(go.Scattermapbox(
        mode = "markers+lines",
        lon = Xe,
        lat = Ye,
        marker = {'size': 5},
        line = {'width': 1, 'color': 'red'})
    )

    fig.update_layout(
        margin ={'l':0,'t':0,'b':0,'r':0},
        mapbox = {
            'style': "open-street-map",
            'center': {'lon': mean(g.vs['lon']), 'lat': mean(g.vs['lat'])},
            'zoom': 7})

    return fig

def populate_rank(g, measures_value):
    top = [top_n_indices(ms, ms.shape[0]) for ms in measures_value]
    for i, _ in enumerate(measures_value):
        measures_value[i][top[i]] = (top[i].shape[0] + 1 - np.array(range(1, top[i].shape[0] + 1))) / top[i].shape[0]
    return np.sum(measures_value, axis=0) 