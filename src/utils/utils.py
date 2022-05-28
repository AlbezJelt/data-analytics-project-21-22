import igraph as ig
import itertools as it

def layout_geo(g: ig.Graph) -> ig.Layout:
    return ig.Layout(it.zip_longest(g.vs['lat'], g.vs['lon']))
