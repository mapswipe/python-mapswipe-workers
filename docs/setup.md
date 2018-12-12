# Setup

To setup the Mapswipe back end you need to setup a [Firebase instance](https://firebase.google.com/) and use Docker to install and run it.


## Firebase

In [Firebase](https://firebase.google.com/) following [database rules](https://console.firebase.google.com/project/_/database/msf-mapswipe/rules) need to be applied:

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
            "completedCount" : {
              ".write": "auth != null",
            }
          },
        ".indexOn": ["distributedCount", "completedCount"]
        }
      },
      "imports" : {
        ".read" : false,
        ".write" : true
      },
     "projects" : {
        ".write": false,
        ".read" : true,
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


## Docker

### 1. Clone Repository

- `git clone https://github.com/mapswipe/python-mapswipe-workers.git`
- `cd python-mapswipe-workers`
- for current development branch: `git checkout benni.new-project-types`


### 2. Configuration

Provide a config file, the Firebase ServiceAccountKey and optionally an environment file for Postgres.

- add your passwords etc. to `cfg/config.cfg`
    - you can use the template `cfg/your_ServiceAccountKey` for this.
- add your firebase `cfg/ServiceAccountKey.json`
    - you can get it from your firebase instance [Admin SDK](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk).
- if you want to use a local psql instance provide an `.env` file with:
    ```
    POSTGRES_PASSWORD=your_psql_password
    POSTGRES_USER=mapswipe_workers
    POSTGRES_DB=mapswipe
    ```

### 3. Run Docker Compose

- `docker-compose up -d`


## Useful commands

* `docker ps -a`: list all containers and check status
* `docker image ls`: list all docker images
* `docker-compose build --no-cache import`: rebuild the image for a specific container (here: import), e.g. after changing some settings like `sleep_time`
* `docker exec -it import bash `: open shell in a running container (here: import)
* `tail -100 ./logs/run_import.log`: show logs of container
* `docker stats`: show memory usage, CPU consumption for all running containers


## Update a container 

How to update a container (e.g. after changing something in python-mapswipe-workers).

1. `git pull`: get changes from github
2. `docker-compose build --no-cache import`: build a new docker image for the container you need to update
3. `docker stop import`
4. `docker-compose up -d import`
