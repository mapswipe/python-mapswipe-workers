# This image contains Python 3 and the latest pre-compiled version of GDAL
# Based on Debian (Including apt-get update && upgrade)
FROM thinkwhere/gdal-python

# create directories for config, logs and data
RUN mkdir -p $XDG_CONFIG_HOME/mapswipe_workers/
RUN mkdir -p /var/log/
RUN mkdir -p /var/lib/mapswipe_workers/
RUN mkdir -p /usr/local/mapswipe-workers/

# copy mapswipe workers repo from local repo
WORKDIR /usr/local/mapswipe-workers/
COPY mapswipe_workers/ .
COPY requirements.txt .
COPY setup.py .
COPY config/ $XDG_CONFIG_HOME/mapswipe_workers/

# Install dependencies and mapswipe-workers
# RUN python setup.py install
RUN pip install .

# we don't use a CMD here, this will be defined in docker-compose.yaml
