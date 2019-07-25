# Setup

This document describes how to setup all the parts of the MapSwipe back-end.

1. Firebase Setup
2. Postgres Setup
3. MapSwipe Workers Setup


For all those setups our main repository is requiered:

```bash
git clone https://github.com/mapswipe/python-mapswipe-workers.git
cd python-mapswipe-workers
```


To run Mapswipe Workers you need to:

1. Clone the repository
2. Setup a [Firebase Project](https://firebase.google.com/)
3. Provide custom configurations
4. Use [Docker](https://www.docker.com/) to run Mapswipe Workers


## Firebase Setup

### Credentials

* firebase project id
* firebase web api key
* firebase admin sdk service account file
* firebase database rules json file


### 2. Setting up a Firebase Project

You have to manually set up your firebase instance at very first. Start with creating your [**Firebase Project**](https://firebase.google.com/) and follow these steps:
1. Login
2. Add project
3. Create Database: `> Develop > Database > Create Database`
4. Get **Web API Key**: `> Settings > Project settings > General`. Add the web api key to the `.env` file.
5. Download **Service Account Key**: `> Settings > Project settings > Service accounts > Firebase Admin SDK > Generate new private key`. Rename the downloaded json file to `serviceAccountKey.json` and move it to `mapswipe_workers/config/`



### Deployment of Database Rules and Fuctions

The Firebase setup consists of two parts:

- Firebase Database Rules (`database.rules.json`)
- Firebase Functions (`functions/`)

```bash
docker run node --name node
```
To deploy them to the Firebase instance the Firebase CLI is required. Please refer to the official docs on how to install the Firebase CLI ([https://firebase.google.com/docs/cli/](https://firebase.google.com/docs/cli/#install_the_firebase_cli))

After installation of the Firebase CLI change working directory into the `firebase` directory and initialize a Firebase project:

```
cd firebase
firebase init
```

Select Database and Functions. Do not overwrite any existing files.

To deploy database rules and functions to your Firebase project run:

```
firebase deploy
```

https://firebase.google.com/docs/cli/#install_the_firebase_cli


## Postgres Setup

In the `postgres` directory is an `initdb.sql` file for initializing a Postgres database.

When running Postgres using the provided Dockerfile it will setup a Postgres database during the build.
Then a Postgres user, password and database name has to be defined in an environment file (`.env`) in the same directory as the `docker-compose.yaml` file (root):

```env
POSTGRES_USER=mapswipe
POSTGRES_PASSWORD=mapswipe
POSTGRES_DB=mapswipe
```

Set custom user and password.

To run the Postgres Docker container:

```
docker-compose up -d postgres
```

The Postgres instance will be exposed to `localhost:5432`.


## MapSwipe Workers Setup

To run MapSwipe Workers a valid configuration (`config/configuration.json`) and the Firebase Service Account Key (`config/serviceAccountKey.json`) is required (See Firebase Setup section).

Among other variables following are mandatory:

- bing maps url
- bing maps api key
- digital globe url
- digital globe api key
- sinergise url
- sinergise api key


These variables are optional:

- slack token
- slack channel
- slack username


### Configuration

Edit the configuration file (`config/example-configuration.json`) and rename it to `configuration.json`.

Example configuration for the Firebase section:

```json
"dev_firebase": {
  "api_key": "TBaSDnrFaJEWgVaslf-vpt5dg53fAjfdsV-1uaig",
  "auth_domain": "dev-mapswipe.firebaseapp.com",
  "database_url": "https://dev-mapswipe.firebaseio.com",
  "storage_bucket": "dev-mapswipe.appspot.com"
}
```


### Run MapSwipe Workers

```bash
docker-compose up -d mapswipe_workers
```


### Update Mapswipe Workers

How to update Mapswipe Workers:

```
git pull
docker-compose up --build -d mapswipe_workers
```


## Lets Encrypt

Install certbot:

```bash
apt-get install certbot
```


Create certificates:

```bash
certbot certonly \
    --standalone \
    --domain dev-api.mapswipe.org \
    --domain dev-managers.mapswipe.org \
    --agree-tos \
    --email herfort@uni-heidelberg.de \
    --non-interactive
```


Enable and start certbot systemd timer for renewal of certificates:

```bash
systemctl enable certbot.timer
systemctl start certbot.timer
# To check if certbot.timer is enabled run:
systemctl list-units --type timer | grep certbot
```


Add renewal post hook to reload nginx after certificate renwal:

```bash
mkdir -p /etc/letsencrypt/renewal-hooks/deploy
cat <<EOM >/etc/letsencrypt/renewal-hooks/deploy/nginx
#!/usr/bin/env bash

docker container restart nginx
EOM
chmod +x /etc/letsencrypt/renewal-hooks/deploy/nginx
```

<!--
Using the certbot plugin dnf-google:

```bash
sudo apt install python3-certbot-dns-google
certbot certonly \
    --dns-google \
    --dns-google-credentials certbot.json \
    --server https://acme-v02.api.letsencrypt.org/directory \
    --domain *.mapswipe.org \
    --agree-tos \
    --email herfort@uni-heidelberg.de
    --non-interactive
```


Dockerize it:

```bash
sudo docker run -it --rm --name certbot \
            -v "/etc/letsencrypt:/etc/letsencrypt" \
            -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
            certbot/dns-google certonly \
            --dns-google \
            --dns-google-credentials ~/.secrets/certbot/google.json \
            --domain *.mapswipe.org \
            --server https://acme-v02.api.letsencrypt.org/directory \
            --agree-tos \
            --email herfort@uni-heidelberg.de \
            --non-interactive
```
-->


## Manager Dashboard

```
docker-compose up -d manager_dashboard
```


## API

```
docker-compose up -d api
```


## Debugging

Check if your Docker Containers are running: `docker ps`

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
