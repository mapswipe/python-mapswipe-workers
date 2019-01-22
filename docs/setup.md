# Setup

To run Mapswipe Workers you need to:
1. Clone the repository
2. Setup a [Firebase Project](https://firebase.google.com/)
3. Provide custom configurations
4. Use [Docker](https://www.docker.com/) to run Mapswipe Workers


## 1. Clone Repository

- `git clone https://github.com/mapswipe/python-mapswipe-workers.git`
- `cd python-mapswipe-workers`
- for current development branch: `git checkout benni.new-project-types`


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
- Put the downloaded Firebase Service Account Key into the folder `cfg` of the cloned Mapswipe Workers Project.


## 3. Configuration

Provide a config file, the Firebase ServiceAccountKey and an environment file for Postgres.


### config.cfg

Edit following variables in the config file (`cfg/your_config_file.cfg`) and rename it to `config.cfg`.

**Change**:
- line 2: `"psql":{` to `"dev_psql":{`
- line 9: `"firebase":{` to `"dev_firebase":{`

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
  "service_account": "./cfg/dev-mapswipe_serviceAccountKey.json"
```


### .ENV

Create an **Environment file** (`.env`) at root of the project (`python-mapswipe-workers/`) with following variables:
```env
POSTGRES_USER=mapswipe-workers
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mapswipe
```
 Set custom user and password.


### docker-compose.yaml

<!-- TODO -->

**Change service > postgres > ports**:
- line 16: `"5432:5432"` to `"5433:5432"`


## 4. Installing Mapswipe Workers using Docker

Start the **Docker Daemon**:
- `systemctl start docker`

Run **Docker Compose**:
- `docker-compose up -d`

Usefull **Docker Commands**:
- `docker ps -a`: list all containers and check status
- `docker image ls`: list all docker images
- `docker-compose build --no-cache import`: rebuild the image for a specific container (here: import), e.g. after changing some settings like `sleep_time`
- `docker exec -it import bash `: open shell in a running container (here: import)
- `tail -100 ./logs/run_import.log`: show logs of container
- `docker stats`: show memory usage, CPU consumption for all running containers
- `docker system prune`: clean up any resources — images, containers, volumes, and networks — that are dangling (not associated with a container)


## Debugging

**Where can I find the logs?**:
- `docker logs import`
- logs folder


## Update

How to update a container (e.g. import):

1. `git pull`: get changes from github
2. `docker-compose build --no-cache import`: build a new docker image for the container you need to update
3. `docker stop import`
4. `docker-compose up -d import`
