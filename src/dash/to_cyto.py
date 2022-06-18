import py4cytoscape as py4
import igraph as ig

g = ig.Graph.Read('./data/graphs/april2022_Lspace.graphml')

cyto_graph = py4.create_network_from_igraph(g)

py4.networks.export_network('./data/graphs/april2022_Lspace.json', type='cyjs', network=cyto_graph)