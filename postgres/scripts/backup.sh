#!/bin/bash

SSH_REMOTE_HOST=username@hostname
PGUSER="backup"
PGDATABASE="mapswipe"
PGPASSWORD="backupuserpassword"

# Create a ssh tunnel in the background and save PID
ssh -Cfo ExitOnForwardFailure=yes -NL 1111:localhost:5432 ${SSH_REMOTE_HOST}
PID=$(pgrep -f 'NL 1111:')

mkdir $(date +%Y%m%d) && cd "$_"

PGPASSWORD=$PGPASSWORD pg_dump \
    --dbname=$PGDATABASE \
    --username $PGUSER \
    --host localhost \
    --port 1111 \
    --schema=public \
    | gzip | split -b 100m - mapswipe.sql.gz

kill ${PID}
