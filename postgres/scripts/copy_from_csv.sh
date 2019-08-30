#!/bin/bash

USER="mapswipe_workers"
NAME="mapswipe"

for entity in projects groups tasks users results
do
    docker cp ${entity}.csv mapswipe_postgres:/${entity}.csv
    docker cp copy_${entity}_from_csv.sql mapswipe_postgres:/copy_${entity}_from_csv.sql
    docker exec -t mapswipe_postgres psql -U ${USER} -d ${NAME} -a -f /copy_${entity}_from_csv.sql
done


