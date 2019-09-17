# Configuration Reference
This document describes all configuration details used by the python-mapswipe-workers. By the end of this document the following configuration files will be set up:

* `.env`
* `mapswipe_workers/config/configuration.json`
* `mapswipe_workers/config/serviceAccountKey.json`
* `manager_dashboard/manager_dashboard/js/app.js`
* `firebase/.firebaserc`

## Google APIs & Services Credentials
The python-mapswipe workers use a bunch of services provided by Google Cloud Platform. It's best to start to configure all api keys we need later directly from the beginning in Google APIs & Services.
1. Open [Google APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Create API key for MapSwipe workers:
    * set name of api key to `mapswipe-workers`
    * set Application restrictions > IP addresses > set IP addresse of mapswipe workers server`
    * set API restrictions > Restrict Key > Identity Toolkit API
3. Create API key for Manager Dashboard:
    * set name of api key to `manager-dashboard`
    * set Application restrictions > HTTP referrers > set HTTP referrer of managers dashboard (e.g. `https://apps.mapswipe.org`)
    * set API restrictions > Restrict Key > Identity Toolkit API and Cloud Functions API
4. Also make sure to configure the API keys for the App side here.

## Firebase
Firebase is a central part of MapSwipe. In our setup we use *Firebase Database* and *Firebase Functions*.

The `mapswipe_workers` module use the [Firebase Python SDK](https://firebase.google.com/docs/reference/admin/python) to access *Firebase Database* services as administrator, you must generate a Firebase Service Account Key in JSON format. You can get it from Firebase.
1. In the Firebase console, open Settings > Service Accounts.
2. Click Generate New Private Key
3. Store the JSON file under `mapswipe_workers/config/serviceAccountKey.json`

The `mapswipe_workers` module further use the [Firebase Database REST API](https://firebase.google.com/docs/reference/rest/database) to access *Firebase Database* either as a "normal" user or "project manager".

For both things to work you need to add your `database_name` in the configuration file. For the the REST API add also the previously generated *mapswipe_workers* `api_key`. (Check the *Google APIs & Services Credentials* section again if you don't have it.) The firebase section in `mapswipe_workers/config/configuration.json` should look like this now:

```json
"firebase": {
  "database_name": "your_database_name",
  "api_key": "your_firebase_api_key"
}
```

The `manager_dashboard` module


The `firebase` module

## Postgres
The MapSwipe workers write data to a postgres data base and generate files for the api based on views in postgres. You need to provide information on postgres in your `mapswipe_workers/config/configuration.json`.:

```json
"postgres": {
  "host": "postgres",
  "port": "5432",
  "database": "mapswipe",
  "username": "mapswipe_workers",
  "password": "your_mapswipe_db_password"
  },
```

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
The MapSwipe workers use sentry to capture exceptions. You can find your project’s DSN in the “Client Keys” section of your “Project Settings” in Sentry. Check [Sentry's documentation](https://docs.sentry.io/error-reporting/configuration/?platform=python) for more information. You need to provide information on Sentry in your `mapswipe_workers/config/configuration.json`.:

```json
"sentry": {
  "dsn": "your_sentry_dsn_value"
  }
```

## Slack (optional)
The MapSwipe workers send messages to slack when a project has been created successfully, the project creation failed or an exception during mapswipe_workers cli occurred. You need to add a slack token to use slack messaging. You can find out more from [Python slackclient's documentation](https://github.com/slackapi/python-slackclient) how to get it. You need to provide information on Slack in your `mapswipe_workers/config/configuration.json`.:

```json
"slack": {
  "token": "your_slack_token",
  "channel": "your_slack_channel",
  "username": "your_slack_username"
  },
```

