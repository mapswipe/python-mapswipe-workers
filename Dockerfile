FROM thinkwhere/gdal-python

# copy mapswipe workers repo from local repo
WORKDIR /python-mapswipe-workers
COPY ./ .

# create directories for data and logs if they don't exist
RUN mkdir -p  logs
RUN mkdir -p data

# Install dependencies and mapswipe-workers
RUN python setup.py install

# we don't use a CMD here, this will be defined in docker-compose.yaml
