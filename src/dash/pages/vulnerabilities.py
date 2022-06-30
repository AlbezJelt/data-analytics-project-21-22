import dash
from dash import html, dcc
import utils
import igraph as ig
import dash_bootstrap_components as dbc
import pickle

dash.register_page(__name__)

with open('./data/plots/april2022_Lspace_robustness.pickle', 'rb') as f:
    robustness = pickle.load(f)

with open('./data/plots/april2022_Lspace_average_path_length_robustness.pickle', 'rb') as f:
    l_robustness = pickle.load(f)

def layout(): 
    return html.Div(
        className='container-fluid page-container',
        children=[
            dcc.Markdown("""
                # Network vulnerabilities

                This section shows how the network changes its structure by responding to different types of attacks, exploiting **percolation theory**. 
                Attacks are made by **removing nodes that are assigned to a certain measure of centrality**. 
                Iteratively one percent of the nodes that maximize that measure are removed, so it is recalculated. 
                The attack ends when there are no more nodes to remove or the measure cannot be further reduced.

                It has been observed in the literature that the behavior of a complex network under an attack that removes nodes or links 
                randomly can differ drastically from a scenario in which attacks are carried out according to certain criteria (measure).

                ### Resilience of the giant component
            """),
            dcc.Graph(
                id='robustness_figure', 
                figure=utils.robustness_figure(robustness), 
                responsive=True,
                style={'padding': '20px'}
            ),
            dcc.Markdown("""
                The above graph shows the evolution of the giant component according to the centrality measures in the legend. 
                Also, the **random baseline removal method** is present.

                The size $\mathrm{S}$ of the giant component is calculated as: 

                $\mathrm{S} = \\frac{\mathrm{N}_{GCC}}{\mathrm{N}} \\times 100$

                where $\mathrm{N}_{GCC}$ represents the number of nodes within the giant component and $\mathrm{N}$ is the total number of nodes.

                ### Average shortest path variation
            """, mathjax=True),
            dcc.Graph(
                id='average_path_length_robustness_figure', 
                figure=utils.average_path_length_robustness_figure(l_robustness), 
                responsive=True,
                style={'padding': '20px'}
            ),
            dcc.Markdown("""
                Trend of the average shortest path versus the number of nodes removed for each measure. 
                The x-axis indicates the percentage of nodes removed, and the y-axis the value of the average shortest path.
            """, mathjax=True)
    ])