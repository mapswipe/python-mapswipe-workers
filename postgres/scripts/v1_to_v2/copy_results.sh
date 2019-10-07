#!/bin/bash

filename='project_ids.txt'

while read project_id;
do

    echo "project_id: $project_id"
    echo "Generate copy_to_csv.sql"
    python3 generate_copy_to_csv.py $project_id

    echo "Run copy_to_csv.sql using copy_restuls_to_csv.sh (Get all results of this projects from old production database)"
    ./copy_results_to_csv.sh

    echo "Run copy_from_csv.sh to insert all results of this project into new production database"
    ./copy_from_csv.sh

done < $filename
