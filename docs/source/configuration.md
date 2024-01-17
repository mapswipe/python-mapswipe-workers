# Configuration Reference

Most of the configuration is stored in environment variables.
At the root of the GitHub repository (in the same directory as `docker-compose.yml`) an example file (`example.env`) with all possible configuration variables exists. To get started copy this file to `.env` (no name is required) and fill in missing variables. The Docker Compose file will access those variables when needed.

> Note: If you want those variables to be accessible as Environment Variables in your current shell (E.g. Inside a Python virtual environment for development.) your need to parse the file and export the variables: `export $(cat .env | xargs)`

In following chapters configuration values and keys are discussed for each part of the MapSwipe Back-end.


## MapSwipe Workers

All configuration values for MapSwipe Workers are stored in environment variables.

Required environment variables are:
### Firebase
- FIREBASE_API_KEY
- FIREBASE_DB
- FIREBASE_TOKEN
- FIREBASE_STORAGE_BUCKET
- GOOGLE_APPLICATION_CREDENTIALS

### Postgres DB
- POSTGRES_DB
- POSTGRES_HOST
- POSTGRES_PASSWORD
- POSTGRES_PORT
- POSTGRES_USER

### OSMCha

- OSMCHA_API_KEY

### Optional environment variables:
- SLACK_CHANNEL
- SLACK_TOKEN
- SENTRY_DSN

For satellite imagery access to at least one provider is needed. Define the API key as environment variable:
- IMAGE_BING_API_KEY
- IMAGE_MAPBOX_API_KEY
- IMAGE_MAXA_PREMUIM_API_KEY
- IMAGE_MAXAR_STANDARD_API_KEY
- IMAGE_ESRI_API_KEY
- IMAGE_ESRI_BETA_API_KEY

> Notes: When deploying using `docker` or `docker-compose` `POSTGRES_HOST` should have the value `postgres` and the Service Account Key (`serviceAccountKey.json`) should be copied to `mapswipe_workers/serviceAccountKey.json` so that during the build of the image the file can by copied by Docker.

### Elaboration

**Firebase**: MapSwipe Workers use the Firebase Python SDK and the Firebase REST API. Both require the database name (`FIREBASE_DB`) and the API-Key from the Firebase instance. The Firebase Python SDK does also need a Service Account Key. The path to this file is set in the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

**Postgres**: MapSwipe Workers writes data to a Postgres database and generate files for the API based data in Postgres.

**OSMCha**: MapSwipe Workers enriches some Projects with data from OSM changelogs which are requested from OSMCha. Create an account, you will find you api key in your profile e.g. `Token 589adf125234a`

**Sentry (optional)**: MapSwipe workers use sentry to capture exceptions. You can find your project’s DSN in the “Client Keys” section of your “Project Settings” in Sentry. Check [Sentry's documentation](https://docs.sentry.io/error-reporting/configuration/?platform=python) for more information.

**Slack (optional)**: The MapSwipe workers send messages to slack when a project has been created successfully, the project creation failed or an exception gets raised. refer to [Python slackclient's documentation](https://github.com/slackapi/python-slackclient) how to get a Slack Token.

**Imagery:** MapSwipe uses satellite imagery provided by Tile Map Services (TMS).
If you are not familiar with the basic concept have a look at [Bing's documentation](https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system).


## Postgres

Required environment variables are (Those are the same as needed by MapSwipe Workers):
- POSTGRES_DB
- POSTGRES_HOST
- POSTGRES_PASSWORD
- POSTGRES_PORT
- POSTGRES_USER

> Notes: When deploying using `docker` or `docker-compose` `POSTGRES_HOST` should have the value `postgres`.


### Postgres Backup

On details of how the back-up works please refer to [Postgres Backup](backup.html).

Required environment variables are:
- WALG_GS_PREFIX

To gain access to Google Cloud Storage another Service Account Key is needed. Again refer to [Postgres Backup](backup.html) on how to create this file.
The Service Account Key (`serviceAccountKey.json`) should be saved to `postgres/serviceAccountKey.json`


## Manager Dashboard

Please refer to the official [documentation](https://firebase.google.com/docs/web/learn-more#config-object) if you set up your own firebase. 
Otherwise you can request guidance on the settings from the mapswipe team. The structure of your app.js should look like below.

### Firebase
- MANAGER_DASHBOARD_FIREBASE_API_KEY
- MANAGER_DASHBOARD_FIREBASE_AUTH_DOMAIN
- MANAGER_DASHBOARD_FIREBASE_DATABASE_URL
- MANAGER_DASHBOARD_FIREBASE_PROJECT_ID
- MANAGER_DASHBOARD_FIREBASE_STORAGE_BUCKET
- MANAGER_DASHBOARD_FIREBASE_MESSAGING_SENDER_ID
- MANAGER_DASHBOARD_FIREBASE_APP_ID

### Sentry
- MANAGER_DASHBOARD_SENTRY_DSN
- MANAGER_DASHBOARD_SENTRY_TRACES_SAMPLE_RATE

## Community Dashboard

### Django API
- COMMUNITY_DASHBOARD_GRAPHQL_CODEGEN_ENDPOINT
- COMMUNITY_DASHBOARD_GRAPHQL_ENDPOINT

### Sentry
- COMMUNITY_DASHBOARD_SENTRY_DSN
- COMMUNITY_DASHBOARD_SENTRY_TRACES_SAMPLE_RATE

### Elaboration
**COMMUNITY_DASHBOARD_GRAPHQL_CODEGEN_ENDPOINT**: Graphql endpoint of the Django API. Eg: https://api.example.com/graphql/
**COMMUNITY_DASHBOARD_GRAPHQL_ENDPOINT**: Same as COMMUNITY_DASHBOARD_GRAPHQL_CODEGEN_ENDPOINT

## Django API

All configuration values for Django are stored in environment variables.

Required environment variables are:
### Django
- DJANGO_SECRET_KEY
- DJANGO_ALLOWED_HOST

### Optional environment variables:
- DJANGO_SENTRY_DSN
- DJANGO_SENTRY_SAMPLE_RATE
- DJANGO_RELEASE
- Postgres (NOTE: Database configuration are pulled from postgres configuration directly in docker-compose files.)
    - DJANGO_DB_NAME
    - DJANGO_DB_USER
    - DJANGO_DB_PWD
    - DJANGO_DB_HOST
    - DJANGO_DB_PORT

### Elaboration
**DJANGO_SECRET_KEY**: A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
**DJANGO_SENTRY_SAMPLE_RATE**: Sample rate by which sentry send transaction metadata. Value should be between 0 to 1. https://docs.sentry.io/platforms/python/guides/django/configuration/sampling/


## NGINX

The configuration for nginx is defined in `nginx/nginx.conf.template` file.

### Domains
- NGINX_MAIN_DOMAIN
- NGINX_DJANGO_DOMAIN
- NGINX_MANAGER_DASHBOARD_DOMAIN
- NGINX_COMMUNITY_DASHBOARD_DOMAIN

> NOTE: Make sure the used domain have valid certificates in /etc/letsencrypt/
### Elaboration
**NGINX_MAIN_DOMAIN**: Domain for main mapswipe static api server.
**NGINX_DJANGO_DOMAIN**: Domain for django web server.
**NGINX_MANAGER_DASHBOARD_DOMAIN**: Domain for manager dashboard.
**NGINX_COMMUNITY_DASHBOARD_DOMAIN**: Domain for community dashboard.
