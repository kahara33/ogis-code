# syntax=docker/dockerfile:1
FROM busybox

ARG WORKDIR=/home/araya
WORKDIR ${WORKDIR}

# Copy pre-built database files into mounted volumes.
COPY ./data/2024-01-18/csv/ ./rag-tab-data/csv/
COPY ./data/2024-01-18/json/ ./rag-tab-data/json/
COPY ./data/2024-01-18/sample.sqlite3 ./rag-tab-data/tables.sqlite3
COPY ./data/2024-01-18/sample.xlsx ./rag-tab-data/tables.xlsx
COPY ./data/2024-02-29/ ./rag-txt-data/
