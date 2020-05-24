#!/bin/bash

# Run this script like this:
# PGPASSWORD=password SSH_REMOTE_HOST=username@hostname bash -c "./backup.sh"

# SSH_REMOTE_HOST=username@hostname
# PGPASSWORD="backupuserpassword"
PGUSER="backup"
PGDATABASE="mapswipe"

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
