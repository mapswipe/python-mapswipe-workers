# Deployment Overview

The MapSwipe Back-End is deployed using Docker.
Every part of the back-end has a Dockerfile.
All parts/ Dockerfiles come together in the docker-compose file.

To setup the whole ecosystem of MapSwipe Workers it is easier to first make sure every part is configured and all keys are in place.

MapSwipe utilizes a bunch of Google Cloud services:

- [Firebase](https://firebase.google.com/) project with Realtime Database and Functions
    - Create a project
    - Create a database: `> Develop > Database > Create Database`
- [Google Cloud Storage](https://cloud.google.com/storage/) for backup of Postgres

[Configuration](configuration.md) describes all needed configuration and credentials.

[Installation](installation.md) describes step-by-step how to setup the backend for the first time.


## Continuous deployment using Ansible and Travis

Travis is setup to automatically deploy a new version of MapSwipe Back-End to the server once it run successfully.
This is done by using Travis script deployment (https://docs.travis-ci.com/user/deployment/script/). Travis simply calls the `deploy.sh` script found at the root directory of MapSwipe Workers.
To be able to connect to the MapSwipe server the Travis instance uses an encrypted SSH private key (Which can be found in the directory `travis/`).

In the `deploy.sh` script an Ansible Playbook is run (https://docs.ansible.com/ansible/latest/index.html). Ansible is an automation tool which utilizes a SSH connection (`ansible/ansible.cfg`) to run commands defined in the Playbook (`ansible/playbook.yml`) on hosts defined in the Inventory (`ansible/inventory.yml`).

## Continuous Deployment with Github Actions
We use an encrypted service account key file. The file has been generated with this commands:

`openssl enc -aes-256-cbc -e -p -nosalt -in=ci-mapswipe-firebase-adminsdk-80fzw-ebce84bd5b.json -out=ci-mapswipe-firebase-adminsdk-80fzw-ebce84bd5b.json.enc`

