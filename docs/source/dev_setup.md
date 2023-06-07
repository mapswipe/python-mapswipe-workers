# Development Setup

In this document some tips and workflows for development are loosely collected. 
Those are independent of the production setup using Docker-Compose. 
A working Firebase Project (Including Firebase Functions and Database Rules) is presupposed. 
Get in touch with the MapSwipe team (e.g. in Slack) to get access to an existing Firebase Instance for development purposes.

Check list:
1. Github: Clone repo from GitHub.
2. Requirements: Install GDAL/OGR and GDAL for Python on your machine.
3. Configuration: Set environment variables and get a Service Account Key File.
4. Database: Set up local Postgres database using Docker.
5. Python-Package: Install MapSwipe Workers Python package.
6. Run MapSwipe Workers.


## Installation

### Clone from GitHub

... and switch to development branch.

```bash
git clone https://github.com/mapswipe/python-mapswipe-workers.git
cd python-mapswipe-workers
git checkout dev
```

### Requirements

MapSwipe Workers requires GDAL/OGR (`gdal-bin`) and GDAL for Python (`libgdal-dev`, `python-gdal`) to be [installed](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html). 
Furthermore, we rely on Docker to set up Postgres.


### Configuration

All configurations values are stored in environment variables. Please refer to the documentation on [Configuration](configuration.html) for further details.

#### Service Account Key

The MapSwipe Workers requires a Service Account Key (`serviceAccountKey.json`) to access Firebase database. 
Request yours from the MapSwipe working group.

The path to the Service Account Key is defined in the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

You could also set up your own Firebase instance. However, this is not recommended. 
If you still want to do it, get your Service Account Key from Firebase from [Google Cloud Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts).


### Database

Setup a local Postgres instance for MapSwipe Workers using the Dockerfile provided for development purposes (`postgres/Dockerfile-dev`). 
The Dockerfile for production (`postgres/Dockerfile`) does need additional setup for build-in backup to Google Cloud Storage, which is not needed for local development. That is why a simplified Dockerfile for development is provided.
Make sure that the specified port is not in use already. If so, adjust the port (also in the `.env` file).

```bash
docker build -t mapswipe_postgres -f ./postgres/Dockerfile-dev ./postgres
docker run -d -p 5432:5432 --name mapswipe_postgres -e POSTGRES_DB="$POSTGRES_DB" -e POSTGRES_USER="$POSTGRES_USER" -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" mapswipe_postgres
```

Or set up Postgres using the `initdb.sql` file in the `postgres/` folder.


### Mapswipe-Workers Python Package

#### Installation

The Python virtual environment needs to be created wiht `system-site-packages` option enabled to get access to GDAL/OGR Python packages.
Also the MapSwipe Workers Python Package needs access to a data directory for logs and data for the API.

```bash
cd mapswipe_workers
python -m venv --system-site-packages venv
source venv/bin/activate
pip install --editable .
pre-commit install
mkdir --parents ~/.local/share/mapswipe_workers
```

#### Usage

```bash
export $(cat .env | xargs)  # See section on Configuration above
mapswipe_workers --help
```

#### Tests

```bash
python -m unittest
```

> Yeah! If you reached this point, you are ready to get into coding. Below you find some more information on Logging, Firebase Functions and Database Backup. However, you don't need this to get started for now.

# Further Information

## Logging

Mapswipe workers logs are generated using the Python logging module of the standard library (See [Official docs](https://docs.python.org/3/library/logging.html) or this [Tutorial](https://realpython.com/python-logging/#the-logging-module). 
To use the logger object import it from the `definitions` module:

```python
from mapswipe_workers.definitions import logger
logger.info('information messages')
logger.waring('warning messages')

# Include stack trace in the log
try:
    do_something()
except Exception:
    logger.exception('Additional information.')
```

Default logging level is Info. To change the logging level edit the logging configuration which is found in the module `definitions.py`. 
Logs are written to STDOUT and `~/.local/share/mapswipe_workers/mapswipe_workers.log`.

Per default logging of third-party packages is disabled. To change this edit the definition module (`mapswipe_workers/defintions.py`). 
Set the `disable_existing_loggers` parameter of the `logging.config.fileConfig()` function to `False`.


## Firebase Functions

Firebase functions are used to increment/decrement or calculate various attribute values which are used by the MapSwipe App. This includes:

- project.progress
- project.numberOfTasks
- project.resultCount
- project.contributorCount
- group.progress
- group.finishedCount
- group.requiredCount
- user.projectContributionCount
- user.groupContribtionCount
- user.taskContributionCount
- user.timeSpentMapping
- user.contibutions{.projectId.groupId.{timestamp, startTime, endTime}}

Those functions will be directly or indirectly triggered by incoming results from the MapSwipe App.

By using Firebase functions those attributes can be calculated in real-time and be accessed by users immediately. 
The use of those functions also reduces the data-transfer between the Firebase Realtime Database and MapSwipe Workers.

On how to setup the development environment and how to deploy functions to the Firebase instance please refer to the official [Guide on Cloud Function for Firebase](https://firebase.google.com/docs/functions/get-started).
For more information refer to the official [Reference on Cloud Function for Firebase](https://firebase.google.com/docs/reference/functions/). 
For example function take a look at this [GitHub repository](https://github.com/firebase/functions-samples).

### OSM OAuth 2
Firebase functions are also used to allow users to login to MapSwipe with their OpenStreetMap account. Refer to [the notes in the app repository](https://github.com/mapswipe/mapswipe/blob/master/docs/osm_login.md) for more information.


## Database Backup

### Firebase

**Manual Backup**

- curl https://<instance>.firebaseio.com/.json?format=export
- ref: https://stackoverflow.com/questions/27910784/is-it-possible-to-backup-firebase-db


### Postgres

**Manual Backup**

- Backup database in compressed splited files of specified size:
    - `pg_dump -U mapswipe -d mapswipe -h localhost -p 5432 | gzip | split -b 100m - mapswipe.pgsql.gz`
    - ref: https://www.postgresql.org/docs/9.1/backup-dump.html
- Copy the backup to your local machine when logged into your local machine:
    - `scp username@ipadress:mapswipe.pgsql.gz* /path/to/destination`
    - ref: https://unix.stackexchange.com/questions/106480/how-to-copy-files-from-one-machine-to-another-using-ssh
- Restore database backup from multiple compressed files
    - `cat mapswipe.pgsql.gz* | gunzip | psql -U mapswipe -d mapswipe -h localhost -p 5432`
