# Installation

This document describes how to setup all the parts of the MapSwipe back-end for the first time.

Please take also a look at our [Configuration Reference](https://mapswipe-workers.readthedocs.io/en/dev/configuration.html) which is a summary of all configurations and keys needed for deployment.

1. Firebase
2. Postgres
3. MapSwipe Workers
4. API
5. Manager Dashboard
6. Lets Encrypt and NEGIX as proxy

For all those setups our main repository is required:

```bash
git clone https://github.com/mapswipe/python-mapswipe-workers.git
cd python-mapswipe-workers
```


## Firebase Setup

Download a Service Account Key File for MapSwipe Workers:

1. In the Firebase console, open Settings > Service Accounts.
2. Click Generate New Private Key
3. Store the JSON file under `mapswipe_workers/config/serviceAccountKey.json`

Configure your API Keys in Google APIs & Services
1. Open [Google APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Create API key for MapSwipe workers:
    * set name of api key to `mapswipe-workers`
    * set Application restrictions > IP addresses > set IP addresse of mapswipe workers server
    * set API restrictions > Restrict Key > Identity Toolkit API
3. Create API key for Manager Dashboard:
    * set name of api key to `manager-dashboard`
    * set Application restrictions > HTTP referrers > set HTTP referrer of managers dashboard
    * set API restrictions > Restrict Key > Identity Toolkit API and Cloud Functions API
4. Also make sure to configure the API keys for the App side here.


### Deploy Database Rules and Functions

The Firebase setup consists of two parts:

- Firebase Database Rules (`firebase/database.rules.json`)
- Firebase Functions (`firebase/functions/`)

To deploy them to the Firebase Project the Firebase Command Line Tools are requiered. They are preinstalled in the provided Docker image (`firebase/Dockerfile`). When running this image the database rules and the functions will be deployed. For this to work a Firebase Token is needed:

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

When running Postgres using the provided Dockerfile it will setup a Postgres database using the `initdb.sql` file during the build.

A Postgres password has to be defined in the environment file (`.env`). E.g:

```
POSTGRES_PASSWORD=mapswipe
```

To run the Postgres Docker container:

```
docker-compose up -d postgres
```

The Postgres instance will be exposed to `localhost:5432`.


## MapSwipe Workers

### Configuration

To run MapSwipe Workers a valid configuration (`config/configuration.json`) and the Firebase Service Account Key (`config/serviceAccountKey.json`) are required.

To authorize MapSwipe Workers to access Firebase database, generate a Firebase Service Account Key in JSON format and save it to `mapswipe_workers/config/serviceAccountKey.json` (See *Firebase Setup* section above for details).

To run the MapSwipe workers you need a configuration file. Edit the provided configuration file template (`config/example-configuration.json`) and rename it to `configuration.json`. In following sections all required configuration will be descibed in detail.


#### Firebase Athentication

The MapSwipe workers use the Firebase Python SDK and the Firebase REST API. The REST API is used for user management only to sign in as "normal" user or "project manager". Both require the `database_name` in your configuration file.

```json
"firebase": {
  "database_name": "your_database_name",
  "api_key": "your_firebase_api_key"
}
```

#### Postgres

The MapSwipe Workers writes data to a Postgres database and generate files for the api based on views in postgres.
Provide only password. Leave the rest at default.

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

The MapSwipe workers use sentry to capture exceptions. You can find your project’s DSN in the “Client Keys” section of your “Project Settings” in Sentry. Check [Sentry's documentation](https://docs.sentry.io/error-reporting/configuration/?platform=python) for more information.

```json
"sentry": {
  "dsn": "your_sentry_dsn_value"
  }
```

#### Slack (optional)

The MapSwipe workers send messages to slack when a project has been created successfully, the project creation failed or an exception during mapswipe_workers cli occurred.
You need to add a slack token to use slack messaging.
You can find out more from [Python slackclient's documentation](https://github.com/slackapi/python-slackclient) how to get it.


```json
"slack": {
  "token": "your_slack_token",
  "channel": "your_slack_channel",
  "username": "your_slack_username"
  },
```


#### Imagery

MapSwipe uses satellite imagery provided by Tile Map Services (TMS).
If you are not familiar with the basic concept have a look at [Bing's documentation](https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system).
Make sure to get api keys for the services you would like to use in your app. 
For each satellite imagery provider add an `api_key` and `url`. 

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

The Manager Dashboard uses the [Firebase JavaScript client SDK](https://firebase.google.com/docs/database/web/start) to access *Firebase Database* service as authenticated as MapSwipe user with project manager credentials. 

1. Open [Google APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Create API key for MapSwipe workers:
    * set name of api key to `mapswipe_workers_api_key`
    * set Application restrictions > IP addresses > set IP addresse of mapswipe workers server
    * set API restrictions > Restrict Key > Identity Toolkit API
3. Create API key for Manager Dashboard:
    * set name of api key to `manager_dashboard_api_key`
    * set Application restrictions > HTTP referrers > set HTTP referrer of managers dashboard (e.g. `https://dev.mapswipe.org`)
    * set API restrictions > Restrict Key > Identity Toolkit API and Cloud Functions API
4. Also make sure to configure the API keys for the App side here.

Project-id refers to the name of your Firebase project (e.g. dev-mapswipe). The firebaseConfig in `mapswipe_dashboard/js/app.js` should look like this now:

```javascript
var firebaseConfig = {
    apiKey: "manager_dashboard_api_key",
    authDomain: "your_project_id.firebaseapp.com",
    databaseURL: "https://your_project_id.firebaseio.com",
    storageBucket: "your_project_id.appspot.com"
  };
```

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


## Lets Encrypt and NGINX

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

> Note: Certbot systemd timer for renewal of certificate will not work for standalone certificates because the service (docker nginx) which occupies port 80 has to be stopped before renewal.

For certificate renewal a cronjob is used:

```bash
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

0 */12 * * * certbot -q renew --pre-hook "docker stop nginx" --post-hook "docker start nginx"
```


### Nginx

NGINX serves the MapSwipe API and Manager Dashboard. If you want these point to a specific domain, make sure to set it up.

Once you got your domain name change `server_name`, `ssl_certificate` and `ssl_certificate_key` in the NGINX configuration file (`nginx/nginx.conf`)

Run NGINX:

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
