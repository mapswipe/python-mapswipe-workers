#!/bin/bash
# This script builds and starts all Docker container for running the Mapswipe ecosystem.
# It is run either manually or by an Ansible Playbook after a successful Travis build.

docker-compose build --no-cache postgres firebase_deploy mapswipe_workers manager_dashboard nginx api
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi

docker-compose up -d --force-recreate postgres firebase_deploy mapswipe_workers manager_dashboard nginx api
if [[ $? = 0 ]]; then
    echo "success"
else
    echo "failure: $?"
    exit
fi
