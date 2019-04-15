# Setup

This document discribes how to run Mapwipe Workers using Docker. For development setup without Docker pleas refer to the [Contributing page](contributing.md).

To run Mapswipe Workers you need to:
1. Clone the repository
2. Setup a [Firebase Project](https://firebase.google.com/)
3. Provide custom configurations
4. Use [Docker](https://www.docker.com/) to run Mapswipe Workers


## 1. Clone Repository

- `git clone https://github.com/mapswipe/python-mapswipe-workers.git`
- `cd python-mapswipe-workers`
- for current development branch: `git checkout dev`


## 2. Setting up a Firebase Project

Create [**Firebase Project**](https://firebase.google.com/):
1. Login
2. Add project

Set **Database Rules**:
1. `> Develop > Database > Create Database`
2. `> Database > Rules`
    - Copy and paste database rules
    - `> Publish`
    - Make sure you are using 'Realtime Database' not 'Cloud Firestore' otherwise your will get an error message (e.g. `Error saving rules - Line 1: mismatched input '{' expecting {'function', 'service', 'rules_version'}`)

```json
{
  "rules": {
    ".read": false,
    ".write": false,
      "groups" : {
        ".write": false,
        ".read" : true,
        "$project_id" : {
          "$group_id" : {
            ".indexOn": ["distributedCount", "completedCount"],
            ".write": "auth != null",
            "completedCount" : {
              ".write": "auth != null",
            }
          },
        ".indexOn": ["distributedCount", "completedCount"]
        }
      },
      "imports" : {
        ".read" : false,
        ".write" : true,
        ".indexOn": ["complete"]
      },
     "projects" : {
        ".write": false,
        ".read" : true,
      },
     "announcement": {
       ".write": true,
      ".read": true,
     },
    "results" : {
      ".write": false,
      ".read" : true,
        "$task_id" : {
          "$user_id" : {
          ".write": "auth != null && auth.uid == $user_id"
          }
        }
      },
      "users": {
      "$uid": {
        ".read": "auth != null && auth.uid == $uid",
        ".write": "auth != null && auth.uid == $uid",
      }
    }     
  }
}
```

Get **Web API Key**:
- `> Settings > Project settings > General`

Download **Service Account Key**:
- `> Settings > Project settings > Service accounts > Firebase Admin SDK > Generate new private key`

Rename the downloaded json file to `serviceAccountKey.json` and move it to `python_mapswipe_workers/config/`


## 3. Configuration

Provide custom configuration and environment file.


### configuration.json

Edit following variables in the configuration file (`config/example-configuration.json`) and rename the file to `configuration.json`:

**postgres**:
- provide usename und password for postgres

**firebase**:
- provide configurations for your Firebase instance
- for example:
```cfg
"dev_firebase":{
  "api_key": "TBaSDnrFaJEWgVaslf-vpt5dg53fAjfdsV-1uaig",
  "auth_domain": "dev-mapswipe.firebaseapp.com",
  "database_url": "https://dev-mapswipe.firebaseio.com",
  "storage_bucket": "dev-mapswipe.appspot.com",
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

Run **Docker Compose**: `docker-compose up -d`

Check if your Docker Containers are running: `docker ps`

Interactive shell session for using e.g. utils: `docker-compose run utils`


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

**configuration.json - FileNotFoundError:** Until fixed the configuration path is hard coded in `mapswipe_workers/definitions.py`. This should work, if Mapswipe Workers is installed and running inside a Docker Container. For custom setup refer to the [contribution page](contribution.md).


## Tips

### Update

How to update a container (e.g. import):

1. `git pull`: get changes from github
2. `docker-compose build --no-cache import`: build a new docker image for the container you need to update
3. `docker stop import`
4. `docker-compose up -d import`


### Usefull Docker Commands

- `docker ps -a`: list all containers and check status
- `docker image ls`: list all docker images
- `docker-compose build --no-cache import`: rebuild the image for a specific container (here: import), e.g. after changing some settings like `sleep_time`
- `docker exec -it import bash `: open shell in a running container (here: import)
- `tail -100 ./logs/run_import.log`: show logs of container
- `docker stats`: show memory usage, CPU consumption for all running containers
- `docker system prune`: clean up any resources — images, containers, volumes, and networks — that are dangling (not associated with a container)

