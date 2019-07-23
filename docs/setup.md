# Setup

This document describes how to run Mapwipe Workers using Docker. For development setup without Docker please refer to the [Contributing page](contributing.md).

To run Mapswipe Workers you need to:

1. Clone the repository
2. Setup a [Firebase Project](https://firebase.google.com/)
3. Provide custom configurations
4. Use [Docker](https://www.docker.com/) to run Mapswipe Workers

## Credentials we need during that process:
### Firebase
* firebase project id
* firebase web api key
* firebase admin sdk service account file
* firebase database rules json file

### Postgres
* postgres username
* postgres password
* posgres host
* postgres port

### Nginx
* server config file

### Imagery
* bing maps url
* bing maps api key
* digital globe url
* digital globe api key
* sinergise url
* sinergise api key

### Slack (optional)
* slack token
* slack channel
* slack username

## 1. Clone Repository

- `git clone https://github.com/mapswipe/python-mapswipe-workers.git`
- `cd python-mapswipe-workers`
- for current development branch: `git checkout dev`


## 2. Setting up a Firebase Project
You have to manually set up your firebase instance at very first. Start with creating your [**Firebase Project**](https://firebase.google.com/) and follow these steps:
1. Login
2. Add project
3. Create Database: `> Develop > Database > Create Database`
4. Get **Web API Key**: `> Settings > Project settings > General`. Add the web api key to the `.env` file.
5. Download **Service Account Key**: `> Settings > Project settings > Service accounts > Firebase Admin SDK > Generate new private key`. Rename the downloaded json file to `serviceAccountKey.json` and move it to `python_mapswipe_workers/config/`


## 3. Setting up Firebase database rules and Firebase functions

1. Set **Database Rules**:
  * `> Database > Rules`
  * Copy and paste database rules from `python_mapswipe_workers/config/firebase-rules.json`
  * `> Publish`
  * Make sure you are using 'Realtime Database' not 'Cloud Firestore' otherwise your will get an error message (e.g `Error saving rules - Line 1: mismatched input '{' expecting {'function', 'service', 'rules_version'}`)

2. Set "Firebase Cloud Functions":
  * deploy cloud functions


## 4. Setting up postgres and the python-workers
1. Create Postgresql database and create tables

2. Set up mapswipe worker for creating projects

3. Set up mapswipe worker for transfering data from firebase to postgres

## 3. Configuration

Provide custom configuration and environment file.


### configuration.json

Edit following variables in the configuration file (`config/example-configuration.json`) and rename the file to `configuration.json`:

**postgres**:
- provide username und password for postgres

**firebase**:
- provide configurations for your Firebase instance
- for example:

```json
"dev_firebase": {
  "api_key": "TBaSDnrFaJEWgVaslf-vpt5dg53fAjfdsV-1uaig",
  "auth_domain": "dev-mapswipe.firebaseapp.com",
  "database_url": "https://dev-mapswipe.firebaseio.com",
  "storage_bucket": "dev-mapswipe.appspot.com"
}
```


### .env

Create an **Environment file** (`.env`) at root of the project (`python-mapswipe-workers/`) with following variables:

```env
POSTGRES_USER=mapswipe-workers
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mapswipe
```

Set custom user and password.


## 4. Installing Mapswipe Workers using Docker

Start the **Docker Daemon**: `systemctl start docker`

Run **Docker Compose**: `docker-compose up -d mapswipe_workers postgres`

Check if your Docker Containers are running: `docker ps`



## Update Mapswipe Workers

How to update Mapswipe Workers:

1. `git pull`: get changes from github
2. `docker-compose up --build -d mapswipe_workers`


## Debugging

**Where can I find logs?**

- Logs are written to directly to console and are written to `/var/log/mapswipe_workers.log`
    - take a look at those for logs of already running containers
- To view logs using docker: `docker logs container_name` (eg. `docker logs import`):
    - take a look at those if your container is not running

**ERROR: for postgres during docker-compose:**

- ERROR: for postgres  `Cannot start service postgres: driver failed programming external connectivity on endpoint postgres`
- Probably a postgres instance is already running on Port 5432
- SOLUTION: Change postgres port in your docker-compose file  (`docker-compose.yaml`)
    - docker-compose.yaml: services > postgres > ports: Change `"5432:5432"` to `"5433:5432"`

**Docker containers are always restarting:** Take a look at the docker logs (eg. `docker logs import`). If you get an `Unable to load configuration file at ./cfg/config.cfg. Exiting.` due to `PermissionError: [Errno 13] Permission denied: './cfg/config.cfg'` error message, you probably have SELinux on your system enabled. If so you have to configure (change mount option of volumes) your docker-compose file. Please read the documentation provided by Docker regarding this configuration (https://docs.docker.com/storage/bind-mounts/ Chapter: "Configure the selinux label").


### Usefull Docker Commands

- `docker ps -a`: list all containers and check status
- `docker image ls`: list all docker images
- `docker exec -it mapswipe_workers bash `: open shell in a running container
- `tail -100 ./logs/mapwipe_workers.log`: show logs of container
- `docker stats`: show memory usage, CPU consumption for all running containers
- `docker system prune`: clean up any resources — images, containers, volumes, and networks — that are dangling (not associated with a container)
