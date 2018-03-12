# Simple Python Dockerfile to run tests.
FROM python:3.6


RUN apt-get update
# Upgrade repo for GDAL
# RUN apt-get install python-software-properties
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:ubuntugis/ppa

# Install binary dependencies and GDAL
COPY ./install_gdal.sh .
RUN bash install_gdal.sh


# Install requirements for the first time
COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /home/mapswipe-workers
WORKDIR /home/mapswipe-workers
