#!/bin/bash

export PGDATABSE=$POSTGRES_DB
export PGUSER=$POSTGRES_USER
export PGPASSWORD=$POSTGRES_PASSWORD

wal-g wal-fetch $1 $2
