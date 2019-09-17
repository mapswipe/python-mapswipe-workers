# Installation

This document describes how to setup all the parts of the MapSwipe back-end for the first time.

1. Firebase
2. Postgres
3. MapSwipe Workers
4. API
5. Manager Dashboard

Moreover we will look into:
6. Lets Encrypt

For all those setups our main repository is required:

```bash
git clone https://github.com/mapswipe/python-mapswipe-workers.git
cd python-mapswipe-workers
```

## Check List
You can run the script `test_config.py` to check if you set all the needed variables and file. The script will test the following files:

`.env file`
* postgres password
* firebase token
* wal-g google storage prefix

`mapswipe_workers/config/configuration.json`
* firebase api key, database name configuration
* postgres host, port, database, username, password configuration
* imagery urls and api keys
* slack token, username and channel
* sentry dsn value

`mapswipe_workers/config/serviceAccountKey.json`
* check if file exists

`manager_dashboard/manager_dashboard/js/app.js`
* firebase authDomain, apiKey, databaseUrl, storageBucket

`nginx/nginx.conf`
* server name
* ssl certificates, ssl certificates key

## Firebase Setup

First a Firebase Project and Database has to be created.

1. Login to [Firebase](https://firebase.google.com/)
2. Add a project
3. Create a database: `> Develop > Database > Create Database`

Then, get a Service Account Key File.
1. In the Firebase console, open Settings > Service Accounts.
2. Click Generate New Private Key
3. Store the JSON file under `mapswipe_workers/config/serviceAccountKey.json`

Configure your API Keys in Google APIs & Services
1. Open [Google APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Create API key for MapSwipe workers:
    * set name of api key to `mapswipe-workers`
    * set Application restrictions > IP addresses > set IP addresse of mapswipe workers server`
    * set API restrictions > Restrict Key > Identity Toolkit API
3. Create API key for Manager Dashboard:
    * set name of api key to `manager-dashboard`
    * set Application restrictions > HTTP referrers > set HTTP referrer of managers dashboard
    * set API restrictions > Restrict Key > Identity Toolkit API and Cloud Functions API
4. Also make sure to configure the API keys for the App side here.


### Deploy Database Rules and Functions

The Firebase setup consists of two parts:

- Firebase Database Rules (`firebase/database.rules.json`)
- Firebase Functions (`firbase/functions/`)

To deploy them to the Firebase Project the Firebase Command Line Tools are requiered. They are preinstalled in the provided Docker image (`firebase/Dockerfile`). When running this image the database riles and the functions will be deployed. For this to work a Firebase Token is needed:

1. On a PC with a browser install the Firebase Command Line Tools ([https://firebase.google.com/docs/cli/](https://firebase.google.com/docs/cli/#install_the_firebase_cli))
2. Run `firebase login:ci` to generate a Firebase Token.
3. Save the Firebase Token to `.env` at the root of the cloned MapSwipe Backend repository on the server: `echo "FIREBASE_TOKEN=your_token" >> .env`

Once the Firebase Token is set the database rules and functions will be deployed when running the `firebase_deploy` docker image using `docker-compose`:

```
docker-compose up --build -d firebase_deploy
```

This container needs to run only as long until the `firebase deploy` command inside the Docker container terminates. Use `docker logs firebase_deploy` to find out if the command is still running.

For more information about the Firebase Command Line Tools visit:[https://firebase.google.com/docs/cli/](https://firebase.google.com/docs/cli/#install_the_firebase_cli)


## Postgres Setup

In the `postgres` directory is an `initdb.sql` file for initializing a Postgres database.

When running Postgres using the provided Dockerfile it will setup a Postgres database during the build.
A Postgres password has to be defined in an environment file (`.env`) in the same directory as the `docker-compose.yaml` file (root). E.g:

```
POSTGRES_PASSWORD=mapswipe
```

To run the Postgres Docker container:

```
docker-compose up -d postgres
```

The Postgres instance will be exposed to `postgres:5432` (postgres Docker network)


### Backup

To backup the Postgres MapSwipe database use the `backup.sh` script inside the `./postgres` directory. It will execute a command (`pgdump`) inside the Postgres Docker container and store the backup locally (outside the Docker container).


## MapSwipe Workers
### Configuration
To run MapSwipe Workers a valid configuration (`config/configuration.json`) and the Firebase Service Account Key (`config/serviceAccountKey.json`) are required.

To authorize MapSwipe Workers to access Firebase services, you must generate a Firebase Service Account Key in JSON format. (Check the *Firebase* section to get this key.)

To run the MapSwipe workers you need a configuration file. Edit the provided configuration file template (`config/example-configuration.json`) and rename it to `configuration.json`.

#### Firebase
The MapSwipe workers use the Firebase Python SDK **and** the Firebase REST api. The REST api is used for user management only to sign in as "normal" user or "project manager". Both require the `database_name` in your configuration file. The REST api requires an `api_key`. (Check the *Google APIs & Services Credentials* section to get this key.) You need to provide information on firebase in your `configuration.json`.:

```json
"firebase": {
  "database_name": "your_database_name",
  "api_key": "your_firebase_api_key"
}
```

#### Postgres
The MapSwipe workers write data to a postgres data base and generate files for the api based on views in postgres. You need to provide information on postgres in your `configuration.json`.:

```json
"postgres": {
  "host": "postgres",
  "port": "5432",
  "database": "mapswipe",
  "username": "mapswipe_workers",
  "password": "your_mapswipe_db_password"
  },
```

#### Sentry
The MapSwipe workers use sentry to capture exceptions. You can find your project’s DSN in the “Client Keys” section of your “Project Settings” in Sentry. Check [Sentry's documentation](https://docs.sentry.io/error-reporting/configuration/?platform=python) for more information. You need to provide information on Sentry in your `configuration.json`.:

```json
"sentry": {
  "dsn": "your_sentry_dsn_value"
  }
```

#### Slack
The MapSwipe workers send messages to slack when a project has been created successfully, the project creation failed or an exception during mapswipe_workers cli occurred. You need to add a slack token to use slack messaging. You can find out more from [Python slackclient's documentation](https://github.com/slackapi/python-slackclient) how to get it. You need to provide information on Slack in your `configuration.json`.:

```json
"slack": {
  "token": "your_slack_token",
  "channel": "your_slack_channel",
  "username": "your_slack_username"
  },
```

#### Imagery
MapSwipe uses satellite imagery provided by Tile Map Services (TMS). If you are not familiar with the basic concept have a look at [Bing's documentation](https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system). Make sure to get api keys for the services you would like to use in your app. For each satellite imagery provider add an `api_key` and `url`. You need to provide information on Imagery in your `configuration.json`.:

```json
"imagery": {
  "bing": {
    "api_key": "your_bing_api_key",
    "url": "http://t0.tiles.virtualearth.net/tiles/a{quad_key}.jpeg?g=854&mkt=en-US&token={key}"
    },
  "digital_globe": {
    "api_key": "your_digital_globe_api_key",
    "url": "https://api.mapbox.com/v4/digitalglobe.nal0g75k/{z}/{x}/{y}.png?access_token={key}"
    },
  "sinergise": {
    "api_key": "your_sinergise_api_key",
    "url": "https://services.sentinel-hub.com/ogc/wmts/{key}?request=getTile&tilematrixset=PopularWebMercator256&tilematrix={z}&tilecol={x}&tilerow={y}&layer={layer}"
    }
  }
```

### Run MapSwipe Workers

```bash
docker-compose up -d mapswipe_workers
```


## Manager Dashboard

Get **Web API Key**: `> Settings > Project settings > General`. Add the web api key to the `.env` file.

Make sure to set restrictions correctly:
* https://cloud.google.com/docs/authentication/api-keys#api_key_restrictions
* https://console.cloud.google.com/apis/credentials

```
docker-compose up -d manager_dashboard
```


## API

Currently the API is a simple Nginx server which serves static files. Those files are generated by MapSwipe Workers and shared over a Docker volume with the API Container.

```
docker-compose up -d api
```


## Lets Encrypt

To enable SSL for the API and MapSwipe Manager Dashboard use Certbot to issue standalone certificates.

### Certbot

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
    --email e@mail.org \
    --non-interactive
```


Enable and start Certbot systemd timer for renewal of certificates:

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

### Run Nginx

```bash
docker-compose up -d nginx
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