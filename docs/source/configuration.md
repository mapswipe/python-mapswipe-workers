# Configuration Reference

Most of the configuration is stored in environment variables.
At the root of the GitHub repository (in the same directory as `docker-compose.yml`) an example file (`example.env`) with all possible configuration variables exists. To get started copy this file to `.env` (no name is required) and fill in missing variables. The Docker Compose file will access those variables when needed.

> Note: If you want those variables to be accessible as Environment Variables in your current shell (Eg. Inside a Python virtual environment for development.) your need to parse the file and export the variables: `export $(cat .env | xargs)`

In following chapters configuration values and keys are discussed for each part of the MapSwipe Back-end.


## MapSwipe Workers

All configuration values for MapSwipe Workers are stored in environment variables.

Required environment variables are:
- FIREBASE_API_KEY
- FIREBASE_DB
- POSTGRES_DB
- POSTGRES_HOST
- POSTGRES_PASSWORD
- POSTGRES_PORT
- POSTGRES_USER

Optional environment variables are:
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

In addition to get access to Firebase a Service Account Key is required.
The path the Service Account Key is defined in:
- GOOGLE_APPLICATION_CREDENTIALS

> Notes: When deploying using `docker` or `docker-compose` `POSTGRES_HOST` should have the value `postgres` and the Service Account Key (`serviceAccountKey.json`) should be copied to `mapswipe_workers/serviceAccountKey.json` so that during the build of the image the file can by copied by Docker.


### Elaboration

**Firebase**: MapSwipe Workers use the Firebase Python SDK and the Firebase REST API. Both require the database name (`FIREBASE_DB`) and the API-Key from the Firebase instance. The Firebase Python SDK does also need a Service Account Key. The path to this file is set in the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

**Postgres**: MapSwipe Workers writes data to a Postgres database and generate files for the API based data in Postgres.

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

`manager_dashboard/manager_dashboard/js/app.js`

```
TODO
```


## NGINX

`nginx/nginx.conf`:

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
