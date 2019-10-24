# This image contains Python 3 and the latest pre-compiled version of GDAL
# Based on Debian (Including apt-get update && upgrade)
FROM thinkwhere/gdal-python:3.7-shippable

# Install gdal-bin to get ogr2ogr tool
RUN apt-get update
RUN apt-get install gdal-bin

# create directories for config, logs and data
RUN mkdir -p /usr/share/config/mapswipe_workers/
RUN mkdir -p /usr/local/mapswipe_workers/
RUN mkdir -p /var/log/mapswipe_workers/
RUN mkdir -p /var/lib/mapswipe_workers/
RUN mkdir -p /var/lib/mapswipe_workers/api-data
RUN mkdir -p /var/lib/mapswipe_workers/api-data/agg_results/
RUN mkdir -p /var/lib/mapswipe_workers/api-data/groups/
RUN mkdir -p /var/lib/mapswipe_workers/api-data/history/
RUN mkdir -p /var/lib/mapswipe_workers/api-data/projects/
RUN mkdir -p /var/lib/mapswipe_workers/api-data/results/
RUN mkdir -p /var/lib/mapswipe_workers/api-data/tasks/

# copy mapswipe workers repo from local repo
WORKDIR /usr/local/mapswipe_workers/
COPY mapswipe_workers/ mapswipe_workers/
COPY sample_data/ sample_data/
COPY tests/ tests/
COPY requirements.txt .
COPY setup.py .
COPY config /usr/share/config/mapswipe_workers

# Install dependencies and mapswipe-workers
# RUN python setup.py install
RUN pip install .

# we don't use a CMD here, this will be defined in docker-compose.yaml