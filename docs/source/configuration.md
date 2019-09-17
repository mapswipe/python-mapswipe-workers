# Configuration Reference
This document describes all configuration details used by the python-mapswipe-workers. By the end of this document the following configuration files will be set up:

* `.env`
* `mapswipe_workers/config/configuration.json`  
* `mapswipe_workers/config/serviceAccountKey.json`
* `manager_dashboard/manager_dashboard/js/app.js`
* `nginx/nginx.conf`

## Google APIs & Services Credentials
The python-mapswipe workers use a bunch of services provided by Google Cloud Platform. It's best to start to configure all api keys we need later directly from the beginning in Google APIs & Services.
1. Open [Google APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Create API key for MapSwipe workers:
    * set name of api key to `mapswipe_workers_api_key`
    * set Application restrictions > IP addresses > set IP addresse of mapswipe workers server`
    * set API restrictions > Restrict Key > Identity Toolkit API
3. Create API key for Manager Dashboard:
    * set name of api key to `manager_dashboard_api_key`
    * set Application restrictions > HTTP referrers > set HTTP referrer of managers dashboard (e.g. `https://dev.mapswipe.org`)
    * set API restrictions > Restrict Key > Identity Toolkit API and Cloud Functions API
4. Also make sure to configure the API keys for the App side here.

## Firebase
Firebase is a central part of MapSwipe. In our setup we use *Firebase Database*, *Firebase Database Rules* and *Firebase Functions*. In the documentation we will refer to two elements:
1. `your_project_id`: This is the name of your Firebase project (e.g. *dev-mapswipe*)
2. `your_database_name`: This is the name of your Firebase database. It is very likely that this will be the same as your Firebase project name as well.)

The `mapswipe_workers` module uses the [Firebase Python SDK](https://firebase.google.com/docs/reference/admin/python) to access *Firebase Database* services as administrator, you must generate a Firebase Service Account Key in JSON format. You can get it from Firebase.
1. In the Firebase console, open Settings > Service Accounts.
2. Click Generate New Private Key
3. Store the JSON file under `mapswipe_workers/config/serviceAccountKey.json`

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

## Postgres
The `postgres` module initializes a Postgres database. When running Postgres using the provided Dockerfile it will setup the database during the build. A Postgres password has to be defined in an environment file in the same directory as the `docker-compose.yaml` file (root). Add the following line to your `.env` file:

```bash
POSTGRES_PASSWORD=your_mapswipe_db_password
```

The `mapswipe_workers` module write data to the Postgres database and generate files for the `api` module based on views in Postgres. You need to provide information on Postgres in your `mapswipe_workers/config/configuration.json`.:

```json
"postgres": {
  "host": "postgres",
  "port": "5432",
  "database": "mapswipe",
  "username": "mapswipe_workers",
  "password": "your_mapswipe_db_password"
  },
```

## Postgres Backup
We back up the Postgres database using [Wal-G](https://github.com/wal-g/wal-g) and [Google Cloud Storage](https://console.cloud.google.com/storage). You could also set it up using another cloud storage service.

First, create a new cloud storage bucket:
1. Google Cloud Platform > Storage > Create Bucket
2. Choose a bucket name, e.g. `your_project_id_postgres_backup`
3. Select storage location > `Multi-Region` > `eu`
4. Select storage class > `Coldline`

Then, generate a Google Cloud Service Account Key:
1. Google Cloud Platform > IAM & Management > Service Accounts
2. Create new Service Account > Select Name > e.g. `your_project_id_postgres_backup`
3. Select Role > `Storage-Administrator`

```bash
GCS_Link_URL=https://console.cloud.google.com/storage/browser/your_project_id_postgres_backup
GCS_Link_for_gsutil=gs://your_project_id_postgres_backup
```

## Nginx
The `nginx` module serves the MapSwipe API and Manager Dashboard. If you want these point to a specific domain, make sure to set it up. In our setup we use Google domains. Other tools will work similar.

Once you got your domain name add it to `nginx/nginx.conf`:

```
server_name your_domain.org;
```

To enable SSL for the API and MapSwipe Manager Dashboard we use [Certbot](https://certbot.eff.org/) to issue standalone certificates using [Let's Encrypt](https://letsencrypt.org/).

## Imagery
MapSwipe uses satellite imagery provided by Tile Map Services (TMS). If you are not familiar with the basic concept have a look at [Bing's documentation](https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system). Make sure to get api keys for the services you would like to use in your app. For each satellite imagery provider add an `api_key` and `url`. You need to provide information on Imagery in your `mapswipe_workers/config/configuration.json`.:

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

## Sentry (optional)
The `mapswipe_workers` module uses sentry to capture exceptions. You can find your project’s DSN in the “Client Keys” section of your “Project Settings” in Sentry. Check [Sentry's documentation](https://docs.sentry.io/error-reporting/configuration/?platform=python) for more information. You need to provide information on Sentry in your `mapswipe_workers/config/configuration.json`.:

```json
"sentry": {
  "dsn": "your_sentry_dsn_value"
  }
```

## Slack (optional)
The `mapswipe_workers` module sends messages to slack when a project has been created successfully, the project creation failed or an exception during mapswipe_workers cli occurred. You need to add a slack token to use slack messaging. You can find out more from [Python slackclient's documentation](https://github.com/slackapi/python-slackclient) how to get it. You need to provide information on Slack in your `mapswipe_workers/config/configuration.json`.:

```json
"slack": {
  "token": "your_slack_token",
  "channel": "your_slack_channel",
  "username": "your_slack_username"
  },
```

