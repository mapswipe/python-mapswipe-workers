#!/bin/bash

export PGDATABASE=$POSTGRES_DB
export PGUSER=$POSTGRES_USER
export PGPASSWORD=$POSTGRES_PASSWORD

wal-g backup-push /var/lib/postgresql/data
