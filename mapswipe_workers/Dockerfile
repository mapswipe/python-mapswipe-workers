# This image contains Python 3 and the latest pre-compiled version of GDAL
# Based on Debian (Including apt-get update && upgrade)
FROM thinkwhere/gdal-python:3.7-shippable

# Install gdal-bin to get ogr2ogr tool
RUN apt-get update
RUN apt-get --yes install gdal-bin

# create directories for config, logs and data
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

# copy mapswipe workers repo from local repo
WORKDIR $repo_dir
COPY mapswipe_workers/ mapswipe_workers/
COPY sample_data/ sample_data/
COPY tests/ tests/
COPY requirements.txt .
COPY setup.py .
COPY config $config_dir

# Install dependencies and mapswipe-workers
# RUN python setup.py install
RUN pip install .

# we don't use a CMD here, this will be defined in docker-compose.yaml
