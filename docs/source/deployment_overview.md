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
