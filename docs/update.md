# Update Module Documentation

The update module updates the progress and number of contributors for MapSwipe projects stored in the firebase projects table.

## Authentification Configuration and Requirements
To properly run the update process you need the following credentials:
* access to firebase
* access to mapswipe mysql database

The default configuration is stored in [auth.py](../cfg/auth.py). You can adapt to your own settings by providing a `config.cfg` file in the same folder as the auth.py script. You can use the [template](../cfg/your_config_file.cfg) for this.

## How to run update
You can run the complete update script like this:
* `python run_update.py`
* `python run_update.py -mo not_finished`
* `python run_update.py -mo user_list -p 124 303 5519`

Parameters:
* `-p` or `--user_project_list`: project id as integer. Only projects corresponding to the provided ids will be downloaded and/or updated.
* `-m` or `--modus`: chose which projects to update. Options: `all`, `not_finished`, `active` (default), `user_list`
* `-l` or `--loop`: if this option is set, the import will be looped
* `-m` or `--max_iterations`: the maximum number of imports that should be performed in integer
* `-s` or `--sleep_time`: the time in seconds for which the script will pause in beetween two imports

PM2 Process Manager settings:
* we can use pm2 process manager to loop the script
* a pm2 configuration is provided in `loop_update_module.json`
* currently we start the update process every 900 seconds (15 minutes)
* you can monitor the process on the server like this:
```
sudo su
pm2 list
tail -100 /data/python-mapswipe-workers/update_module/project_update.log
```

The logs should look like this:
```
...
05-25 12:15:11 DEBUG    "GET /projects/13513/progress.json?shallow=true HTTP/1.1" 200 2
05-25 12:15:11 WARNING  update progress in firebase for project 13513 successful
05-25 12:15:11 WARNING  log progress to file for project 13513 successful
05-25 12:15:11 WARNING  finished project progress update for projects: ['13516', '13517', '13518', '13509', '13513'], 43.408776 sec.
05-25 12:15:11 WARNING  update finished and max iterations reached. sleeping now for 900 sec.
```

## Submodules
### Update Project Contributors
How to run:
* `python update_project_contributors.py`
* `python update_project_contributors.py -p 124 303 5519`

Parameters:
* `-p` or `--projects`: project id as integer. Only projects corresponding to the provided ids will be downloaded and/or updated.

### Update Project Progress
How to run:
* `python update_project_progress.py`
* `python update_project_progress.py -p 124 303 5519`

Parameters:
* `-p` or `--projects`: project id as integer. Only projects corresponding to the provided ids will be downloaded and/or updated.
