# This image contains Python 3 and the latest pre-compiled version of GDAL
# Based on Debian (Including apt-get update && upgrade)
FROM thinkwhere/gdal-python:3.7-shippable

# create directories for config, logs and data
RUN mkdir -p /usr/share/config/mapswipe_workers/
RUN mkdir -p /usr/local/mapswipe_workers/
RUN mkdir -p /var/log/mapswipe_workers/
RUN mkdir -p /var/lib/mapswipe_workers/
RUN mkdir -p /var/lib/mapswipe_workers/aggregated_results_by_task_id/
RUN mkdir -p /var/lib/mapswipe_workers/aggregated_results_by_project_id_and_date/
RUN mkdir -p /var/lib/mapswipe_workers/aggregated_progress_by_project_id_and_date/
RUN mkdir -p /var/lib/mapswipe_workers/aggregated_results_by_user_id_and_date/

# copy mapswipe workers repo from local repo
WORKDIR /usr/local/mapswipe_workers/
COPY mapswipe_workers/ mapswipe_workers/
COPY requirements.txt .
COPY setup.py .
COPY config /usr/share/config/mapswipe_workers

# Install dependencies and mapswipe-workers
# RUN python setup.py install
RUN pip install .

# we don't use a CMD here, this will be defined in docker-compose.yaml
