# apt-get install -y software-properties-common
# add-apt-repository -y ppa:ubuntugis/ppa
apt-get update -y
apt-get install -y build-essential
apt-get install -y gcc
apt-get install -y gdal-bin
apt-get install -y python3-dev
apt-get install -y -q libgdal1-dev
apt-get install -y -q libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
apt-get install -y libgdal1h
apt-get install -y python3-gdal
gdalinfo --version
