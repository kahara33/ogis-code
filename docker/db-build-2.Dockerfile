# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION} as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# The current directory in the image.
ARG WORKDIR=/home/araya
WORKDIR ${WORKDIR}

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN pip install --upgrade pip setuptools wheel
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    python -m pip install .
ENV PYTHONPATH "${PYTHONPATH}:${WORKDIR}/src"

# Copy the source code into the container.
COPY . .

ARG HOST_RAG_TAB_PATH
COPY ./${HOST_RAG_TAB_PATH} ${WORKDIR}/rag-tab-data/tables.xlsx
# Build the SQL database for RAG.
ENV RAG_TAB_PATH="${WORKDIR}/rag-tab-data/tables.xlsx"
RUN python src/rag_tabular

ENV RAG_TXT_PATH="${WORKDIR}/rag-txt-data/IPA_2018-2019.txt"
COPY ./data/2024-02-29/ ./rag-txt-data/
