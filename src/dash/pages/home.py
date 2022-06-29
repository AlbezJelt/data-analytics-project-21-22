import dash
from dash import html, dcc
import utils
import igraph as ig
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

g = ig.Graph.Read('./data/graphs/april2022_Lspace.graphml')

layout = html.Div(
    className='container-fluid page-container',
    children=[
        dcc.Markdown('''
            # About this project

            This dashboard is intended to interactively show the structural properties of trenord's rail network. 
            Through the sidebar on the left, it is possible to access the different features offered.

            ### Built with
            This work was possible thanks to Python and the following libraries:

            * [Dash](https://dash.plotly.com/) to create the dashboard.
            * [Plotly](https://plotly.com/) to create all the graphs embedded with dash.
            * [Pandas](https://vuejs.org/) to process the data feeded to the graphs.

            You can check out all the source code in this [github repository](https://github.com/AlbezJelt/data-analytics-project-21-22), containing all the data pipeline, analytics and 
            a technical exhaustive report.  

            ### Downloads
            You can directly download the underling analyzed networks in GraphML format by right clicking on this links and selecting "Save link as...":

            * [april2022.graphml](./april2022.graphml)
            * [april2022_Lspace.graphml](./april2022_Lspace.graphml)

        '''),
        dcc.Graph(id='graph', figure=utils.mapbox(g), responsive=True, style={'padding': '20px'}),
        dcc.Markdown("""
            ## About Trenord

            Founded on May 3, 2011 by the two current shareholders, [Ferrovie Nord Milano](https://en.wikipedia.org/wiki/Ferrovie_Nord_Milano) (FNM) and [Trenitalia](https://en.wikipedia.org/wiki/Trenitalia), 
            [Trenord](https://www.trenord.it/en/) is one of the most important companies in the European **rail local public transport**, both in terms of size and capillarity of the service.

            **214 million passengers** traveled with Trenord in 2019 using the **2,300 daily trips** that serve the whole of Lombardy, 
            7 provinces of neighboring regions, the Canton of Ticino and Malpensa International Airport.
            Their trains reach **460 stations** spread over a railway network of approximately **2,000 kilometers**. 
            The capillarity of the Trenord service affects 77% of Lombard municipalities (where 92% /of citizens live) which have a railway station within a radius of 5 km.
        """)
])