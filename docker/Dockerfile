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

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN pip install --upgrade pip setuptools wheel
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    python -m pip install .
ENV PYTHONPATH "${PYTHONPATH}:${WORKDIR}/src"

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code  into the container.
COPY . .

# Describe (but not actually expose) the port that the app will listen on.
EXPOSE 8501


ENV RAG_TAB_PATH="${WORKDIR}/rag-tab-data/tables.xlsx"
ENV RAG_TXT_PATH="${WORKDIR}/rag-txt-data/IPA_2018-2019.txt"

# Run the application.
ENTRYPOINT ["streamlit", "run", "app/🏠_ホーム.py"]
