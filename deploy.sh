#!/bin/bash
# Deploy to dev server.
# This script is called by Travis.
ansible-playbook -i ansible/inventory.yml ansible/playbook.yml
