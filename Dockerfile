FROM jupyter/scipy-notebook:latest

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN git config --global --add safe.directory /workspaces/data-analytics-project-21-22

EXPOSE 5000