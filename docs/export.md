# Export Module

The export module gets data from firebase and mysql and saves it as json files. The following files are created:
* `projects.json`: contains all project information as in firebase projects table
* `stats.json`: contains information on total number of users, total distance mapped, total contributions
* `users.json`: contains information on all users as in firebase users table
* `124.json`, `303.json`, ...: contain project results

## Authentification Configuration and Requirements
To properly run the update process you need the following credentials:
* access to firebase
* access to mapswipe mysql database

The default configuration is stored in [auth.py](../cfg/auth.py). You can adapt to your own settings by providing a `config.cfg` file in the same folder as the auth.py script. You can use the [template](../cfg/your_config_file.cfg) for this.

## How to run update
You can run the complete update script like this:
* `python run_export.py`
* `python run_export.py -mo not_finished`
* `python run_export.py -mo user_list -p 124 303 5519`

Parameters:
* `-p` or `--user_project_list`: project id as integer. Only projects corresponding to the provided ids will be downloaded and/or updated.
* `-m` or `--modus`: chose which projects to update. Options: `all`, `not_finished`, `active` (default), `user_list`
* `-o` or `--output_path`: output directory in which the json files will be saved. Default: `/var/www/html`
* `-l` or `--loop`: if this option is set, the import will be looped
* `-m` or `--max_iterations`: the maximum number of imports that should be performed in integer
* `-s` or `--sleep_time`: the time in seconds for which the script will pause in beetween two imports

PM2 Process Manager settings:
* we can use pm2 process manager to loop the script
* a pm2 configuration is provided in `loop_export_module.json`
* currently we start the update process every 900 seconds (15 minutes)
* you can monitor the process on the server like this:
```
sudo su
pm2 list
tail -100 /data/python-mapswipe-workers/export_module/export_data.log
```

The logs of the script in pm2 should look like this:
```
05-25 12:12:39 WARNING  start project results export for project: 13517
05-25 12:12:39 WARNING  project is in firebase projects table and has all attributes: 13517
05-25 12:12:39 WARNING  project exists in firebase: 13517
05-25 12:12:40 WARNING  got results information from mysql for project: 13517. rows = 15727
05-25 12:12:40 WARNING  wrote results to json file for project: 13517. outfile = /var/www/html/projects/13517.json
05-25 12:12:40 WARNING  start project results export for project: 13509
...
05-25 12:12:45 WARNING  got user information from firebase.
05-25 12:12:45 WARNING  exported users.json file: /var/www/html/users.json
05-25 12:12:45 WARNING  computed stats based on user information from firebase.
05-25 12:12:45 WARNING  exported stats.json file: /var/www/html/stats.json
05-25 12:12:45 WARNING  finished users and stats export, 1.052970 sec.
```


## Submodules
### Export Project Results
How to run:
* `python export_project_results.py`
* `python export_project_results.py -p 124 303 5519`
Output:
* `124.json`, `303.json`, `5519.json`, ...

Parameters:
* `-p` or `--projects`: project id as integer. Only projects corresponding to the provided ids will be downloaded and/or updated.
* `-o` or `--output_path`: output directory in which the json files will be saved. Default: `/var/www/html`

### Export Projects
How to run:
* `python export_projects.py`
Parameters:
* `-o` or `--output_path`: output directory in which the json files will be saved. Default: `/var/www/html`
Output:
* `projects.json`

### Export Users and Stats
How to run:
* `python export_users_and_stats.py`
Parameters:
* `-o` or `--output_path`: output directory in which the json files will be saved. Default: `/var/www/html`
Output:
* `users.json`
* `stats.json`
