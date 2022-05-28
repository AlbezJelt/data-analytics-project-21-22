FROM jupyter/scipy-notebook:latest

COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/

RUN pip install --quiet --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

ENV PYTHONPATH "${PYTHONPATH}:/workspaces/data-analytics-project-21-22/src/utils"

EXPOSE 5000