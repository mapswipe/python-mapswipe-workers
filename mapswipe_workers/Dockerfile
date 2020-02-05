# https://github.com/OSGeo/gdal/tree/master/gdal/docker
# Image includes python3.6, gdal-python, gdal-bin
FROM osgeo/gdal:ubuntu-small-latest

# Set C.UTF-8 locale as default (Needed by the Click library)
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install pip
RUN apt-get update
RUN apt-get --yes install python3-pip

# Create user mapswipe
RUN groupadd --system mapswipe
RUN useradd --create-home --no-log-init --system --gid mapswipe mapswipe

# Create directory for logs and make it accessable for the user mapswipe
RUN mkdir --parents /var/log/mapswipe_workers
RUN chown mapswipe /var/log/mapswipe_workers

# Change user to mapswipe
USER mapswipe
WORKDIR /home/mapswipe

# Create directories for config, data and logs
RUN mkdir --parents .config/mapswipe_workers
RUN mkdir --parents .local/share/mapswipe_workers/api

# Copy mapswipe workers repo from local repo
COPY mapswipe_workers/ mapswipe_workers/
COPY sample_data/ sample_data/
COPY tests/ tests/
COPY requirements.txt .
COPY setup.py .
COPY config/ .config/mapswipe_workers/

# Update setuptools and install mapswipe-workers with dependencies (requirements.txt)
RUN pip3 install --upgrade setuptools
RUN pip3 install .

# Add platform-specific user binary directory for Python applications to $PATH
ENV PATH="$PATH:/home/mapswipe/.local/bin"

# Don't use a CMD here, this will be defined in docker-compose.yaml
