# https://github.com/OSGeo/gdal/tree/master/gdal/docker
# Image includes python3.6, gdal-python, gdal-bin
FROM osgeo/gdal:ubuntu-small-latest

# Set C.UTF-8 locale as default (Needed by the Click library)
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install pip
RUN apt-get update
RUN apt-get --yes install python3-pip

WORKDIR /root

# Create directories for config, data and logs
RUN mkdir --parents .local/share/mapswipe_workers

# Copy mapswipe workers repo from local repo
COPY mapswipe_workers/ mapswipe_workers/
COPY python_scripts/ python_scripts/
COPY sample_data/ sample_data/
COPY requirements.txt .
COPY setup.py .
COPY serviceAccountKey.json .

# Update setuptools and install mapswipe-workers with dependencies (requirements.txt)
RUN pip3 install --upgrade setuptools
RUN pip3 install .

# Don't use a CMD here, this will be defined in docker-compose.yaml
