# Backup

For Postgres backups [WAL-G](https://github.com/wal-g/wal-g) is used. "WAL-G is an archival restoration tool for Postgres".

For more information please refer to the official docs of [WAL-G](https://github.com/wal-g/wal-g) and the official docs of [Postgres](https://www.postgresql.org/docs/current/continuous-archiving.html) on write ahead log (WAL). Current setup took inspiration from this [blog post](https://www.fusionbox.com/blog/detail/postgresql-wal-archiving-with-wal-g-and-s3-complete-walkthrough/644/).


## Backup setup

The WAL-G backup setup is integrated into the Postgres Docker image. It will do a baseline backup of the database to Google Cloud Storage every day utilizing a cron job and `wal-g backup-push`. After that the Postgres will push WAL (Write-Ahead Log) files to Google Cloud Storage regularly using  `wal-g wal-push`. For exact commands please take a look at following script:
- `postgres/wal-g/make_basebackup.sh`
- `postgres/wal-g/archive_command.sh`

WAL-G is installed alongside Postgres. See the Dockerfile of Postgres (`postgres/Dockerfile`) for details. In the docker-compose postgres command (`docker-compose.yml`) archive parameter of postgres are set needed to make archives.


## Restore setup

The WAL-G restore setup is realized in a dedicated Docker image (`postgres/Dockerfile-restore_backup`). It will create a new Postgres database cluster, fetch latest backup using `wal-g backup-fetch` and create a `recovery.conf` file in the new cluster during Docker build. `recovery.conf` is used by Postgres during first start to get the `restore_command`. Again the exact commands are to be found in `postgres/wal-g/restore_command.sh`. During first start Postgres will get WALs from backup server and restore the database.


## Configuration

To store backups in Google Cloud Storage, WAL-G requires that this variable be set: `WALG_GS_PREFIX` to specify where to store backups (eg. `gs://x4m-test-bucket/walg-folder`).
Please add this to your `.env` file at the root of MapSwipe Back-end (See `.example-env` for environment variables wich needs to be set)

WAL-G determines Google Cloud credentials using application-default credentials like other GCP tools. Get a Service Account Key file (`serviceAccountKey.json`) for your Google Cloud Storage (See [Google Cloud Docs](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)) and save it to `postgres/serviceAccountKey.json`.
