#!/bin/bash

USER="mapswipe_workers"
NAME="mapswipe"

for entity in projects groups tasks users results
do
    psql -h localhost -p 5432 -U ${USER} -d ${NAME} -a -f copy_${entity}_from_csv.sql
done

# Commands if docker postgres port is not exposed:
# docker cp ${entity}.csv mapswipe_postgres:${entity}.csv
# docker cp copy_${entity}_from_csv.sql mapswipe_postgres:copy_${entity}_from_csv.sql
# docker exec -t mapswipe_postgres psql -U ${USER} -d ${NAME} -a -f copy_${entity}_from_csv.sql
