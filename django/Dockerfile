FROM python:3.10-buster

LABEL maintainer="Mapswipe info@mapswipe.org"

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY pyproject.toml poetry.lock /code/

RUN apt-get update -y \
    && apt-get install -y \
        # Used for waiting for postgres db.
        wait-for-it \
        # For postgis
        gdal-bin \
    # Upgrade pip and install python packages for code
    && pip install --upgrade --no-cache-dir pip poetry \
        && poetry --version \
        # Configure to use system instead of virtualenvs
        && poetry config virtualenvs.create false \
        && poetry install --no-root \
        # Remove installer
        && pip uninstall -y poetry virtualenv-clone virtualenv \
    && apt-get clean -y \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /code/
