# Installation using Docker

## Get Repository from Github
1. `git clone https://github.com/mapswipe/python-mapswipe-workers.git`
2. `cd python-mapswipe-workers`
3. (`git checkout benni.new-project-types`)

## Provide config file and firebase ServiceAccountKey
4. add your passwords etc. to `cfg/config.cfg` (you can use the template `cfg/your_ServiceAccountKey` for this.)
5. add your firebase `cfg/ServiceAccountKey.json` (you can get it from your firebase instance [Admin SDK](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk).)

## Setup things using docker
6. if you want to use a local psql instance provide an `.env` file with:
    ```
    POSTGRES_PASSWORD=your_psql_password
    POSTGRES_USER=mapswipe_workers
    POSTGRES_DB=mapswipe
    ```
7. `docker-compose up -d`

## Further tasks
* `docker ps -a`: list all containers and check status
* `docker image ls`: list all docker images
* `docker-compose build --no-cache import`: re build the image for a specific container (here: import), e.g. after changing some settings like `sleep_time`
* `docker exec -it import bash `: open shell in a running container (here: import)
* `tail -100 ./logs/run_import.log`