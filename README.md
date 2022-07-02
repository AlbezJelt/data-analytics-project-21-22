# Analysis on Trenord Network

Analisis of the rail transport network of Trenord, i.e., the network of the Lombardy region, to study its characteristics and find possible critical points in case of malfunctions, 
through the activities of Network Analysis and Vulnerability Detection.

Link to the dataset: [Transitfeeds](https://transitfeeds.com/p/trenord/724)

# Development environment setup

The development environment is provided with a docker image based on [jupyter/scipy-notebook](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-scipy-notebook).
It doesn't require to manually install any python package (even python itself isn't needed):

1. Install Docker following the [official guide](https://docs.docker.com/get-docker/).

2. Now you can procede in two different ways:
    * (**Reccomended**) Open the project folder with Visual Studio Code, install the [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension, than press F1 to show all commands, find and select Remote-Containers: Reopen in Container.
    * Or build and run the docker image manually.
      ```bash
      docker build -t data-analytics-project-21-22 .
      docker run -it --rm data-analytics-project-21-22
      ```
      In the terminal you should be prompted to open a link in the browser that redirect to a Jupyter Notebook environment.

# Repository structure

The repository is structured in the following way:
- **.devcontainer**: contains the configuration to launch the development container in Visual Studio Code.
- **data**: contains all the datasets (both original and processed) and all the graphs in *GraphML* format.
- **src**: contains all the source code, organized in the following sub folders:
    - **dash**: the dashboard created with Dash.
    - **final_analysin**: network analytics extraction.
    - **preprocessing**: the data preprocessing pipeline.
    - **utils**: utility functions.

# About

Project for 2021/2022 Data Analytics course, master degree in Computer Science, Milano Bicocca.

Development team:
- Alberici Federico, *808058*
- Gherardi Alessandro, *817084*
- Locatelli Simone Giuseppe, *816781*
