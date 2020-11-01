#!/bin/bash
# Deploy to dev server.
# This script is called by Travis.

function bell() {
  while true; do
    echo -e "\a"
    sleep 60
  done
}
bell &

ansible-playbook -i ansible/inventory.yml ansible/playbook.yml

exit $?
