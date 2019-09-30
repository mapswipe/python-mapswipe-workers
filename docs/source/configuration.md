<!--

Then set up a Service Account Key file:
1. Open [Google Cloud Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create a new Service Account Key file:
    * set name (e.g. *dev-mapswipe-workers*)
    * add roles, (e.g. `Storage Admin` and `Firebase Admin`) or use pre-defined role instead (e.g. `Custom Firebase Developer`)
3. Download Key as file:
    * select `.json` and save





## Firebase

Firebase is a central part of MapSwipe. In our setup we use *Firebase Database*, *Firebase Database Rules* and *Firebase Functions*. In the documentation we will refer to two elements:
1. `your_project_id`: This is the name of your Firebase project (e.g. *dev-mapswipe*)
2. `your_database_name`: This is the name of your Firebase database. It is very likely that this will be the same as your Firebase project name as well.)

The `mapswipe_workers` module uses the [Firebase Python SDK](https://firebase.google.com/docs/reference/admin/python) to access *Firebase Database* services as administrator, you must generate a Service Account Key file in JSON format. For this we use the previously generated Service Account Key. (Check the *Google APIs and Services Credentials* section again if you don't have it.) Copy the file to `mapswipe_workers/config/serviceAccountKey.json`.

The `mapswipe_workers` module further uses the [Firebase Database REST API](https://firebase.google.com/docs/reference/rest/database) to access *Firebase Database* either as a normal user or project manager.

For both things to work you need to add your `database_name` in the configuration file. For the the REST API add also the previously generated *mapswipe_workers* api key. (Check the *Google APIs & Services Credentials* section again if you don't have it.) The firebase section in `mapswipe_workers/config/configuration.json` should look like this now:

```json
"firebase": {
  "database_name": "your_database_name",
  "api_key": "mapswipe_workers_api_key"
}
```

The `manager_dashboard` module uses the [Firebase JavaScript client SDK](https://firebase.google.com/docs/database/web/start) to access *Firebase Database* service as authenticated as MapSwipe user with project manager credentials. Add the previously generated *manager-dashboard* api key. (Check the *Google APIs & Services Credentials* section again if you don't have it.) Project-id refers to the name of your Firebase project (e.g. dev-mapswipe). The firebaseConfig in `mapswipe_dashboard/js/app.js` should look like this now:

```javascript
var firebaseConfig = {
    apiKey: "manager_dashboard_api_key",
    authDomain: "your_project_id.firebaseapp.com",
    databaseURL: "https://your_project_id.firebaseio.com",
    storageBucket: "your_project_id.appspot.com"
  };
```

The `firebase` module uses the [Firebase Command Line Interface (CLI) Tools](https://github.com/firebase/firebase-tools) to access *Firebase Database Rules* and *Firebase Functions*. You need a firebase token. Here's how you generate it:
1. On a PC with a browser install the Firebase Command Line Tools ([https://firebase.google.com/docs/cli/](https://firebase.google.com/docs/cli/#install_the_firebase_cli))
2. Run `firebase login:ci` to generate a Firebase Token.
3. Save the Firebase Token to `.env` at the root of the cloned MapSwipe Backend repository: `echo "FIREBASE_TOKEN=your_token" >> .env`
4. You should have an entry for the firebase token in your `.env` now:

```bash
FIREBASE_TOKEN="your_token"
```

-->

# Configuration Reference

This document provides details on all required configuration files:

- `.env file`
    * postgres password
    * firebase token
    * wal-g google storage prefix
- `mapswipe_workers/config/configuration.json`
    * firebase: api-key, databaseName
    * postgres: host, port, database, username, password
    * imagery: urls, api keys
    * slack: token, username, channel
    * sentry: dsn value
- `mapswipe_workers/config/serviceAccountKey.json`
    * check if file exists
- `manager_dashboard/manager_dashboard/js/app.js`
    * firebase: authDomain, apiKey, databaseUrl, storageBucket
- `nginx/nginx.conf`
    * server name
    * ssl certificates, ssl certificates key

You can run the script `test_config.py` to check if you set all the needed variables and file. The script will test the following files:


## .env

The environment file (`.env`) contains all variables needed by services running in Docker container.

```.env
POSTGRES_PASSWORD=password

# Google Cloud Storage path for backups of Postgres
WALG_GS_PREFIX=gs://x4m-test-bucket/walg-folder

# Token for deployment of Firebase Rules and Functions
FIREBASE_TOKEN=firebase_token

GOOGLE_APPLICATION_CREDENTIALS=google_application_credentials
```


## MapSwipe Workers - Configuration

`mapswipe_workers/config/configuration.json`:

```json
{
    "postgres": {
        "host": "postgres",
        "port": "5432",
        "database": "mapswipe",
        "username": "mapswipe_workers",
        "password": "your_mapswipe_db_password"
    },
    "firebase": {
        "database_name": "your_firebase_database_name",
        "api_key": "your_firebase_api_key"
    },
    "imagery":{
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
    },
    "slack": {
        "token": "your_slack_token",
        "channel": "your_slack_channel",
        "username": "your_slack_username"
    },
    "sentry": {
        "dsn": "your_sentry_dsn_value"
    }
}
```


## NGINX

```
server {
    listen 80;
    server_name dev.mapswipe.org;

    location / {
        return 301 https://$host$request_uri;
    }
}


server {
    listen 443 ssl;

    ssl_certificate /etc/letsencrypt/live/dev.mapswipe.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dev.mapswipe.org/privkey.pem;

    server_name dev.mapswipe.org;

    location /api/ {
        proxy_pass  http://api:80/;
    }

    location /api {
        rewrite ^ /api/ permanent;
    }

    location /manager_dashboard/ {
        proxy_pass  http://manager_dashboard:80/;
    }

    location /manager_dashboard {
        rewrite ^ /manager_dashboard/ permanent;
    }

    location / {
        rewrite ^ /manager_dashboard/ permanent;
    }
}
```

## Postgres Backup
We back up the Postgres database using [Wal-G](https://github.com/wal-g/wal-g) and [Google Cloud Storage](https://console.cloud.google.com/storage). You could also set it up using another cloud storage service.

First, create a new cloud storage bucket:
1. Google Cloud Platform > Storage > Create Bucket
2. Choose a bucket name, e.g. `your_project_id_postgres_backup`
3. Select storage location > `Multi-Region` > `eu`
4. Select storage class > `Coldline`

We need to access Google Cloud Storage. For this we use the previously generated Service Account Key. (Check the *Google APIs and Services Credentials* section again if you don't have it.) Copy the file to `postges/serviceAccountKey.json`.

```bash
GCS_Link_URL=https://console.cloud.google.com/storage/browser/your_project_id_postgres_backup
GCS_Link_for_gsutil=gs://your_project_id_postgres_backup
```
