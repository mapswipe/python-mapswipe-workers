#!/bin/bash
# Export v1 MapSwipe data to CSV

USER=mapswipe-workers
NAME=mapswipe
SSH_REMOTE_HOST=schaub@35.243.198.52

# Create a ssh tunnel in the background and save PID
ssh -Cfo ExitOnForwardFailure=yes -NL 1111:localhost:5432 ${SSH_REMOTE_HOST}
PID=$(pgrep -f 'NL 1111:')

psql -p 1111 -h localhost -U ${USER} -d ${NAME} -a -f copy_to_csv.sql
psql -p 1111 -h localhost -U ${USER} -d ${NAME} -a -f copy_results_to_csv.sql

kill ${PID}
