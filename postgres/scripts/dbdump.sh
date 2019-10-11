#!/bin/bash

SSH_REMOTE_HOST=username@111.11.111.0
PGUSER="backup"
PGDATABASE="mapswipe"
PGPASSWORD="backupuserpassword"

# Create a ssh tunnel in the background and save PID
ssh -Cfo ExitOnForwardFailure=yes -NL 1111:localhost:5432 ${SSH_REMOTE_HOST}
PID=$(pgrep -f 'NL 1111:')

PGPASSWORD=$PGPASSWORD pg_dump -d $PGDATABASE -U $PGUSER -h localhost -p 1111 | gzip | split -b 100m - mapswipe.sql.gz

kill ${PID}
