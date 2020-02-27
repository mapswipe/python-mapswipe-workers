# Development Setup

In this document some tips and workflows for development are loosely collected. Those are independend of the production setup using Docker. A working Firebase Project (including Firebase Functions and Database Rules) is presupposed.


## Installation

### Requirements

MapSwipe Workers requires GDAL/OGR (`gdal-bin`) and GDAL for Python (`libgdal-dev`, `python-gdal`) to be installed.


### Clone from GitHub

```bash
git clone https://github.com/mapswipe/python-mapswipe-workers.git
cd python-mapswipe-workers
git checkout dev
```


### Configuration

MapSwipe Workers looks for configuration in `~/.config/mapswipe_workers`. (XDG Base Directory Specification is respected):

Create the configuration directory:
`mkdir --parents ~/.config/mapswipe_workers`

MapSwipe Workers expects three files in the configuration directory:
- `configuration.json`
- `serviceAccountKey.json`
- `logging.cfg`

Please refer to the [configuration](configuration.md) and [setup](setup.md) documentation for further details.

In addition the data directory for MapSwipe Workers needs to be created:
`mkdir --parents ~/.local/share/mapswipe_workers`


### Install MapSwipe Workers Python Package

1. Create a Python virtual environment with `system-site-packages` option enabled to get access to GDAL/OGR Python packages
2. Activate the vitrual environment.
3. Install MapSwipe Workers using pip.
4. Run it.

```bash
python -m venv --system-site-packages venv
source venv/bin/activate
pip install --editable .
mapswipe_workers --help
```


## Postgres

Setup a local Postgres instance for MapSwipe Workers using the provided Dockerfile.

```bash
cd postgres/`
docker build -t mapswipe_postgres Dockerfile-dev
docker run -d -p 5432:5432 --name mapswipe_postgres -e POSTGRES_DB=mapswipe -e POSTGRES_USER=mapswipe_workers -e POSTGRES_PASSWORD=your_password mapswipe_postgres
```

Or set up your own using the `initdb.sql` file in the `postgres/` folder


## Logging

Mapswipe workers logs are generated using the Python logging module of the standard library (See [Official docs](https://docs.python.org/3/library/logging.html) or this [Tutorial](https://realpython.com/python-logging/#the-logging-module). The configuration file of the logging module is located at `~/.config/mapswipe_workers/logging.cfg`. With this configuration a logger object is generated in the `definitions` module (`mapswipe_workers/definitions.py`) and is imported by other modules for writing logs.

```python
from mapswipe_workers.definitions import logger
logger.info('information')
logger.waring('warning')

# Include stack trace in the log
try:
    do_something()
except Exception:
    logger.exception('Additional information.')
```

Default logging level is Info. To change the logging level edit the configuration. Logs are written to STDOUT and `~/.local/share/mapswipe_workers/mapswipe_workers.log`.

Per default logging of third-party packages is disabled. To change this edit the definition module (`mapswipe_workers/defintions.md`). Set the `disable_existing_loggers` parameter of the `logging.config.fileConfig()` function to False.


## Firebase Functions

Firebase functions are used by Mapswipe Workers to increment/decrement or calculate various attribute values wich are used by the Mapswipe App. This includes at the moment:
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

The functions will be triggert by incoming results from the Mapswipe App.

By using firebase functions those attributes can be calculated in real-time and be accessed by users immediately. The use of those functions also reduces the data-transfer between the Firebase Realtime Database and Mapswipe Workers.

On how to setup development enviroment and how to deploy functions to the Firebase instance please refer to the official [Guide on Cloud Function for Firebase](https://firebase.google.com/docs/functions/get-started).
For more information refer to the official [Reference on Cloud Function for Firebase](https://firebase.google.com/docs/reference/functions/). For example function take a look at this [GitHub repository](https://github.com/firebase/functions-samples).


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
