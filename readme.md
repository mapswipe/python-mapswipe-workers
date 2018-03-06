# Python MapSwipe Workers Documentation
If you are new to MapSwipe it might be good to have a look at the [MapSwipe Data Model](mapswipe_data_model.md) first.

The python-mapswipe-workers consist of several python scripts. They do the follwing things:
* create tasks and groups for new imports/projects (import module)
* transfer results from firebase to mysql (transfer results module)
* update progress and contributors for mapswipe projects in firebase (update module)
* export statistics as json files (export_module)

For a more detailed view on what the scripts are doing and how, please have a look at the respective readme.md provided in each folder. There is a [setup.md](setup.md) which describes how to install all requirements.


## Configuration and Authentification
All files related to authentication and configuration can be found in the folder. All relevant information is provided by these files:
* cfg/auth.py
* cfg/your_config_file.cfg
* cfg/your_serviceAccountKey.json

Please provide a file named `config.cfg` with the follwing information. You can use `your_config_file.cfg` as a template for this.

* **mysql**: *database, username, password, host*
* **firebase**: *api_key, auth_domain, database_url, storage_bucket, service_account*
	* To connect to firebase as an admin you need a `serviceAccountKey`. You can get it from your firebase instance [Admin SDK](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk). 
* **imagery**: *bing, digital_globe* (api keys)
	* MapSwipe uses imagery provided by Bing, Digital Globe or other providers. Make sure to get an API key for [Bing](https://www.microsoft.com/en-us/maps/create-a-bing-maps-key) or [Digital Globe Imagery](https://mapsapidocs.digitalglobe.com/docs/access-tokens).
* **slack**: *token, channel, username*
	* If you want the workers to send slack notifications you can create a slack token for your app on this [page](https://api.slack.com/custom-integrations/legacy-tokens).
* **import**: *submission_key*
    * projects imported to firebase will only be processed if the correct submission key is provided
	
The `auth.py` script provides you with the following methods: (Make sure to provide the information required in the `config.cfg` file.)
* `firebase_admin_auth()`: Uses the service account credential to our configuration that will allow our server to authenticate with Firebase as an admin and disregard any security rules. (uses [pyrebase](https://github.com/thisbejim/Pyrebase) library)
* `get_api_key(tileserver)`: Returns the api key for the tileserver specified.
* `get_submission_key(tileserver)`: Returns the submission key.
* `mysqlDB()`: Sets up a connection to your mysql database. (uses [pymysql](https://github.com/PyMySQL/PyMySQL) library)


## Monitoring and Logging
We use the process manager [PM2](http://pm2.keymetrics.io/docs/usage/quick-start/) to monitor the python scripts and restart them once finished. The modules run independently. For each module there is a `.json` file in the `cfg` folder, which specifies the PM2 settings.

* For a general overview have a look at the dashboard of your [Compute Engine](https://console.cloud.google.com/compute/instances).
* Database downloads from firebase are provided [here](https://console.firebase.google.com/project/_/database/usage/last-24h/bandwidth).

To monitor the running processes connect to the Compute Engine and simply use the following commands:
```bash
sudo su
pm2 list
```

You can add your scripts to startup like this:
```bash
sudo su
pm2 startup
pm2 save
```

The modules create logs. You can have a look at these logs like this:
```
tail -100 /data/python-mapswipe-workers/import_module/run_import.log
tail -100 /data/python-mapswipe-workers/transfer_results_module/transfer_results.log
tail -100 /data/python-mapswipe-workers/update_module/run_update.log
tail -100 /data/python-mapswipe-workers/export_module/run_export.log
```
