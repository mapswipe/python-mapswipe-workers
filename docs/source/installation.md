# Installation

This document describes how to setup all the parts of the MapSwipe backend in a production environment.

Please consult the [Configuration Reference](configuration.html) for this setup as well.

1. Firebase
2. Postgres
3. MapSwipe Workers
4. API
5. Manager Dashboard
6. Lets Encrypt and NGINX as proxy

For this setup the main repository is required:

```bash
git clone https://github.com/mapswipe/python-mapswipe-workers.git
cd python-mapswipe-workers
```

## Firebase Setup

Download a Service Account Key File for MapSwipe Workers:

1. In the Firebase console, open Settings > Service Accounts.
2. Click Generate New Private Key, download it and store it to `mapswipe_workers/serviceAccountKey.json`

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

To deploy them to the Firebase Project the Firebase Command Line Tools are required. When running the provided Docker image (`firebase/Dockerfile`) the database rules and the functions will be deployed. For this to work a Firebase Token is needed:

1. On a PC with a browser install the Firebase Command Line Tools ([https://firebase.google.com/docs/cli/](https://firebase.google.com/docs/cli/#install_the_firebase_cli))
2. Run `firebase login:ci` to generate a Firebase Token.
3. Save the Firebase Token to `.env` at the root of the cloned MapSwipe Backend repository on the server: `echo "FIREBASE_TOKEN=your_token" >> .env`

Once the Firebase Token is set the database rules and functions will be deployed when running the `firebase_deploy` Docker image using `docker-compose`:

```
docker-compose up --build -d firebase_deploy
```

This container needs to run only as long until the `firebase deploy` command inside the Docker container terminates. Use `docker logs firebase_deploy` to find out if the command is still running.


## Postgres Setup

In the `postgres` directory is an `initdb.sql` file for initializing a Postgres database.

When running Postgres using the provided Dockerfile it will setup a Postgres database using the `initdb.sql` file during the build.

The Postgres configuration (eg. password) has to be defined in the environment file (`.env`):

```
POSTGRES_PASSWORD=your_password
```

To run the Postgres Docker container:

```
docker-compose up -d postgres
```

The Postgres instance will be exposed to `localhost:5432`.


## MapSwipe Workers


### Configuration


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

To install Certbot follow instructions on https://certbot.eff.org/lets-encrypt/ubuntubionic-other

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

For certificate renewal a cronjob is used. This has to be run as root: `sudo crontab -e`

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
