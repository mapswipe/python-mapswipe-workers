# Development Setup

In this document some tips and workflows for development are loosely collected. Those are independend of the production setup and Docker. A working Firebase Project (including Firebase Functions and Database Rules) is presupposed.


1. Install GDAL (python-gdal)
2. Setup virtual environment with system-site-packages enabled (To get access to GDAL)
    - `python3 -m venv --system-site-packages venv`
3. Activate virtual environment
    - `source venv/bin/activate`
4. Install mapswipe_workers
    - `pip install -e .`
5. Configure MapSwipe Workers as described in the section 'MapSwipe Workers Setup' in the [Setup](setup.md) chapter
    - Make sure configuration and data paths are created and permissions are set as described in the next section [Configuration and data path](#Configurationa_and_data_path).
    - Move the configuration (`config/configuration.json`) and the Service Account Key (`config/serviceAccountKey.json`) to `/usr/share/config/mapswipe_workers/`
6. Setup a postgres instance
    - Use the Docker image of MapSwipe
        - `cd postgres/`
        - `docker build -t mapswipe_postgres .`
        - `docker run -d -p 5432:5432 --name mapswipe_postgres -e POSTGRES_DB=mapswipe -e POSTGRES_USER=mapswipe_workers -e POSTGRES_PASSWORD=your_password mapswipe_postgres`
    - Or set up your own using the `initdb.sql` file in the `postgres/` folder
7. Run Mapswipe Workers using the command: `mapswipe_wokers`
    - eg. `mapswipe_wokers --help`


## Configuration and data path

Mapsipe Workers needs access to three directories:

- CONFIG_PATH (`/usr/share/config/mapswipe_workers/`)
- DATA_PATH (`/var/lib/mapswipe_workers/`)
- LOG_PATH (`/var/log/mapswipe_workers/`)

Make sure those are existing and accessible:

- Use `mkdir DATA_PATH` to create the directory.
- Use `chown -R $USER:$USER PATH` (eg. `chown -R $USER:$USER /user/share/config/mapswipe_workers/`) to give write permission to current user.

Alternatively you can change the PATH variables in `definitions.py` to your desired path. Except of the path for logs. This is defined in `logging.cfg`.


## Logging

Mapswipe workers logs are generated using the Python logging module of the standard library (See [Official docs](https://docs.python.org/3/library/logging.html) or this [Tutorial](https://realpython.com/python-logging/#the-logging-module). The configuration file of the logging module is located at `mapswipe_workers/logging.cfg`. With this configuration a logger object is generated in the `definitions` module (`mapswipe_workers.definitions.py`) and is imported in other modules to write logs.

```python
from mapswipe_workers.definitions import logger
logger.info('information')
logger.waring('warning')

# Include stack trace in the log
try:
    print(something)
except Exception:
    logger.exception('something')
```

Default logging level is Warning. To change the logging level edit the configuration (`mapswipe_workers/logging.cfg`).

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
