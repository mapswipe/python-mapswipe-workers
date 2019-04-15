# Development

In this document some tips and workflows for development and hosting are loosely collected.


## Configuration path and data path

According to the [Filesystem Hierarchy Standard](http://www.pathname.com/fhs/pub/fhs-2.3.html#THEROOTFILESYSTEM) document configuration, logs and data of a programm should be stored at following location:
- logs: `/var/log/mapswipe.log`
- data: `/var/lib/mapswipe/`
- configuration: `/etc/mapswipe/configuration.json`
- cofiguration: `/etc/mapswipe/serviceAccountKey.json`

Depending on user permissions you have to change ownership/permissions (chown) of those directories for the application to work.


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

Firebase functions are used by Mapswipe Workers to calculate or increment attribute values wich are needed by the Mapswipe App. This includes at the moment:
- project.progress
- group.progress
- group.completedCount
- user.contributionCount
- user.distance

To contribute changes to the Firebase Functions please refer to the official (Guide on Cloud Function for Firebase)[https://firebase.google.com/docs/functions/get-started] on how to setup development enviroment and on how to deploy functions to the Firebase instance. For more information refer to the official (Reference on Cloud Function for Firebase)[https://firebase.google.com/docs/reference/functions/]. For example function take a look at this (GitHub repository)[https://github.com/firebase/functions-samples].


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
