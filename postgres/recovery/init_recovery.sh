#!/bin/bash

# Restore base backup.
# Will create a new Database Cluster.
wal-g backup-fetch /var/lib/postgresql/mapswipe LATEST

# Move recovery.conf to cluster to tell postgres where to fetch WAL from.
mv /recovery.conf /var/lib/postgresql/mapswipe/

chown -R postgres:postgres /var/lib/postgresql/mapswipe
chmod 700 /var/lib/postgresql/mapswipe

# Execute command given in Dockerfile ("docker-entrypoint.sh", "postgres").
exec "$@"
