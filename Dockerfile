FROM python:3.6-stretch

# Update base container install
RUN apt-get update
RUN apt-get upgrade -y

# Add unstable repo to allow us to access latest GDAL builds
RUN echo deb http://ftp.uk.debian.org/debian unstable main contrib non-free >> /etc/apt/sources.list
RUN apt-get update

# Existing binutils causes a dependency conflict, correct version will be installed when GDAL gets intalled
RUN apt-get remove -y binutils

# Install GDAL dependencies
RUN apt-get -t unstable install -y libgdal-dev g++

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# This will install latest version of GDAL
RUN pip install GDAL>=2.2.4

# get repository from github
# WORKDIR /data
# RUN git clone https://github.com/mapswipe/python-mapswipe-workers.git
# make sure to use correct branch
# WORKDIR /python-mapswipe-workers
# RUN git checkout benni.new-project-types

# copy mapswipe workers repo from local repo
WORKDIR /python-mapswipe-workers
COPY ./ .

# Make sure to provide a config file and service account key file
# COPY ./cfg/config.cfg ./cfg/
# COPY ./cfg/dev-mapswipe_serviceAccountKey.json ./cfg

# create directories for data and logs
RUN mkdir -p  logs
RUN mkdir -p data

# Install dependencies and mapswipe-workers
RUN python setup.py install

CMD ["python", "run_mapswipe_worker.py", "--modus=development", "--process=import"]


