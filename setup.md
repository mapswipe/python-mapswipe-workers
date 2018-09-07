# Setting everything up
To run the MapSwipe backend we currently use the following setting:
* firebase instance
* google cloud Compute Engine (n1-standard-2 (2 vCPUs, 7.5 GB RAM, 1000 GB SSD))
* google cloud SQL server (MySQL 5.6, 2 vCPUs, 7.5 GB RAM, 50 GB SSD)

## Firebase
In firebase we need to set the [database rules](https://console.firebase.google.com/project/_/database/msf-mapswipe/rules):

```json
{
  "rules": {
    ".read": false,
    ".write": false,
      "groups" : {
        ".write": false,
        ".read" : true,
        "$project_id" : {
          "$group_id" : {
            "completedCount" : {
              ".write": "auth != null",
            }
          },
        ".indexOn": ["distributedCount", "completedCount"]
        }
      },
      "imports" : {
        ".read" : false,
        ".write" : true
      },
     "projects" : {
        ".write": false,
        ".read" : true,
      },
    "results" : {
      ".write": false,
      ".read" : true,
        "$task_id" : {
          "$user_id" : {
          ".write": "auth != null && auth.uid == $user_id"
          }
        }
      },
      "users": {
      "$uid": {
        ".read": "auth != null && auth.uid == $uid",
        ".write": "auth != null && auth.uid == $uid",
      }
    }


  }
}
```

## Compute Engine
On the compute engine we use PM2 to monitor the python scripts, python3 in a virtual environment to run the scripts and we need GDAL for geometry processing.

### Install PM2
```
npm install pm2@latest -g
```

For more information on PM2 go to this [site](http://pm2.keymetrics.io/docs/usage/quick-start/).

### Install Python 3
A good documentation can be found [here](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04).

Ubuntu 16.04 ships with both Python 3 and Python 2 pre-installed. To manage software packages for Python, let’s install pip.

`sudo apt-get install -y python3-pip`

Set up a virtual environment.

```
sudo su
apt-get install -y python3-venv
mkdir /data/environments
cd /data/environments
python3 -m venv mapswipe_workers
```

### Install GDAL

Install `GDAL` at the system level:

     sudo apt-get install libgdal-dev

 Before installing the Python library, you'll need to set up your environment to build it correctly (it needs to know where the system `GDAL` libraries are). Set the following environment variables to do that:

     export CPLUS_INCLUDE_PATH=/usr/include/gdal
     export C_INCLUDE_PATH=/usr/include/gdal

 Finally, install the Python library. You'll need to specify the same version for the Python library as you have installed on the system. Use this to find your system version:

     gdal-config --version

 and install the library via pip with:

     pip3 install GDAL==$VERSION

 or this handy one-liner for both:

     pip3 install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')


 alternatively, you can skip the environment variable exports with the following one-liner that specifies where the gdal headers are included:

     pip3 install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}') --global-option=build_ext --global-option="-I/usr/include/gdal"


### Install the required python packages
```
source /data/environments/mapswipe_workers/bin/activate
pip3 install -r /data/python-mapswipe-workers/requirements.txt
```

### install mapswipe workers package
```
python setup.py install
```

## Cloud SQL
The MySQL database consists of two tables:
* `projects`
* `results`

You can create these tables using `utils/setup_database_tables.py`.

In order for module imports to work, might need to set the project root directory as the PYTHONPATH environment variable: 

    export PYTHONPATH=/data/python-mapswipe-workers
