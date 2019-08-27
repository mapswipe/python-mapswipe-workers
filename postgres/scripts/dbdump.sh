#!/bin/bash

DBUSER="backup"
DBNAME="mapswipe"
DBPASSWD="backupuserpassword"

docker exec -t postgres PGPASSWORD=$DBPASSWD pg_dump -U $DBUSER -d $DBNAME | gzip | split -b 100m - mapswipe.sql.gz
