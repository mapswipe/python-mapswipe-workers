#!/bin/bash
# Export v1 MapSwipe data to CSV

USER=mapswipe_workers
NAME=mapswipe

psql -U ${USER} -d ${NAME} -a -f copy_to_csv.sql
