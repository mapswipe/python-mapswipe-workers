#!/bin/bash
# Deploy to server.
# This script is called by Travis.

function bell() {
  # Print regular to stdout, so that Travis will not abort due to time.
  # travis_wait does not work with script deployment.
  while true; do
    echo -e "\a"
    sleep 60
  done
}
bell &

ansible-playbook -i ansible/inventory.yml ansible/playbook.yml

exit $?  # Return exit code of last command
