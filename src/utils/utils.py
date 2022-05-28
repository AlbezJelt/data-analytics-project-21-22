import igraph as ig
import itertools as it
import numpy as np

def layout_geo(g: ig.Graph) -> ig.Layout:
    return ig.Layout(it.zip_longest(g.vs['lat'], g.vs['lon']))

def top_n_indices(arr: np.ndarray, n: int, sort: bool = True) -> np.ndarray:
    top_n = np.argpartition(arr, -n)[-n:]
    if sort:
        return top_n[np.argsort(arr[top_n])[::-1][:n]]
    else:
        return top_n