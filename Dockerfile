FROM jupyter/scipy-notebook:latest

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 5000