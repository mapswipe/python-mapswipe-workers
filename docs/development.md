# Development

In this document some tips and workflows for development and hosting are loosely collected.


## Firebase

**Manual Backup**
- curl https://<instance>.firebaseio.com/.json?format=export
- ref: https://stackoverflow.com/questions/27910784/is-it-possible-to-backup-firebase-db


## Postgres

**Manual Backup**
- Backup database in compressed splited files of specified size:
    - `pg_dump -U mapswipe -d mapswipe -h localhost -p 5432 | gzip | split -b 100m - mapswipe.pgsql.gz`
    - ref: https://www.postgresql.org/docs/9.1/backup-dump.html
- Copy the backup to your local machine when logged into your local machine:
    - `scp username@ipadress:mapswipe.pgsql.gz* /path/to/destination`
    - ref: https://unix.stackexchange.com/questions/106480/how-to-copy-files-from-one-machine-to-another-using-ssh
- Restore database backup from multiple compressed files
    - `cat mapswipe.pgsql.gz* | gunzip | psql -U mapswipe -d mapswipe -h localhost -p 5432`
