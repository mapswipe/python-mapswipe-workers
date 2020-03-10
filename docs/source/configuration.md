# Configuration Reference

Most of the configuration is stored in environment variables.
At the root of the GitHub repository an example file (`example.env`) with all possible configuration variables exists. To get started copy this file to `.env` and fill in missing variables. Once done source this file to make variables accessible as environment variables: `source .env` to either be used by docker-compose during deployment setup or by MapSwipe Workers directly.

In following chapters configuration values and keys are discussed for each part of the MapSwipe Back-end.


## MapSwipe Workers

All configuration values for MapSwipe Workers are stored in environment variables.

Required environment variables are:
- FIREBASE_API_KEY
- FIREBASE_DB
- GOOGLE_APPLICATION_CREDENTIALS
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

> Notes: When deploying using `docker` or `docker-compose` `POSTGRES_HOST` should have the value `postgres` and the Service Account Key (`serviceAccountKey.json`) should be copied to `mapswipe_workers/serviceAccountKey.json` as described in detail in [Deployment](deployment.md).


## Postgres

Required environment variables are:
- POSTGRES_DB
- POSTGRES_HOST
- POSTGRES_PASSWORD
- POSTGRES_PORT
- POSTGRES_USER


### Postgres Backup

On details of how the back-up works please refer to [Postgres Backup](backup.md).

Required environment variables are:
- WALG_GS_PREFIX

To gain access to Google Cloud Storage another Service Account Key is needed. Again refer to [Postgres Backup](backup.md) on how to create this file.
The Service Account Key (`serviceAccountKey.json`) should be saved to `postgres/serviceAccountKey.json`


### Manager Dashboard

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
