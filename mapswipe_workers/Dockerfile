# https://github.com/OSGeo/gdal/tree/master/gdal/docker
# Image includes python3.6, gdal-python, gdal-bin
FROM osgeo/gdal:ubuntu-small-latest

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install pip
RUN apt-get update
RUN apt-get --yes install python3-pip

# Create directories for config, logs and data
ARG config_dir=/usr/share/config/mapswipe_workers/
ARG repo_dir=/usr/local/mapswipe_workers/
ARG data_dir=/var/lib/mapswipe_workers/
ARG logs_dir=/var/log/mapswipe_workers/

RUN mkdir -p $config_dir
RUN mkdir -p $repo_dir
RUN mkdir -p $logs_dir
RUN mkdir -p $data_dir
RUN mkdir -p $data_dir"api-data"
RUN mkdir -p $data_dir"api-data/agg_results/"
RUN mkdir -p $data_dir"api-data/groups/"
RUN mkdir -p $data_dir"api-data/history/"
RUN mkdir -p $data_dir"api-data/projects/"
RUN mkdir -p $data_dir"api-data/results/"
RUN mkdir -p $data_dir"api-data/tasks/"
RUN mkdir -p $data_dir"api-data/yes_maybe/"
RUN mkdir -p $data_dir"api-data/hot_tm/"

# Copy mapswipe workers repo from local repo
WORKDIR $repo_dir
COPY mapswipe_workers/ mapswipe_workers/
COPY sample_data/ sample_data/
COPY tests/ tests/
COPY requirements.txt .
COPY setup.py .
COPY config $config_dir

# Update setuptools and install mapswipe-workers with dependencies (requirements.txt)
RUN pip3 install --upgrade setuptools
RUN pip3 install .

# Don't use a CMD here, this will be defined in docker-compose.yaml
