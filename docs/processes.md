# Processes

## Import

The import module uses data uploaded to the firebase imports table and creates the respective project information and information regarding groups and tasks.

The import module gets data from firebase and creates the following tables/files:
* `data/project_{id}.kml`: the geometry of the project as provided in the import
* `data/groups_{}.json`: the groups, containing information on tasks, that are uploaded to firebase
* `data/groups_{id}.geojson`: the groups, without further task information, and geometry and extent for each group
* insert a column for each new project in mysql `projects` table


### Authentification Configuration and Requirements

To properly run the update process you need the following credentials:
* access to firebase
* access to mapswipe mysql database

The default configuration is stored in [auth.py](../cfg/auth.py). You can adapt to your own settings by providing a `config.cfg` file in the same folder as the auth.py script. You can use the [template](../cfg/your_config_file.cfg) for this.


### How to run import

You can run the complete import script like this:
* `python run_import.py`
* `python run_import.py -mo development`
* `python run_import.py -mo production`

Parameters:
* `-mo` or `--modus`: chose which mapswipe instance to use. Options: `development` (default), `production`
* `-l` or `--loop`: if this option is set, the import will be looped
* `-m` or `--max_iterations`: the maximum number of imports that should be performed in integer
* `-s` or `--sleep_time`: the time in seconds for which the script will pause in beetween two imports

PM2 Process Manager settings:
* we can use pm2 process manager to loop the script
* a pm2 configuration is provided in `loop_import_module.json`
* currently we start the update process every 900 seconds (15 minutes)
* you can monitor the process on the server like this:
```
sudo su
pm2 list
tail -100 /data/python-mapswipe-workers/export_module/export_data.log
```

The logs should look like this:
```
05-25 12:11:29 WARNING There are no projects to import.
```


### About the Grouping Algorithm

If the terms *group*, *task* and *project* sound not familiar to you in the context of MapSwipe have a look at the [MapSwipe data model](mapswipe_data_model.md) first.

The grouping algorithm creates a `.json` file that can be uploaded into firebase groups table. This file contains also the task information for all tasks within each group. There is no separate file for tasks. All information is stored in the `group_{project_id}.json` file. Basically the grouping workflow contains of these steps:
* load geometry from `.kml`, `.geojson` or `.shp` file (`get_geometry_from_file(input_file)`)
* slice input polygon horizontally (`get_horizontal_slice(extent, geomcol, config['zoom'])`)
    * All created slices will have a height of three tiles
* slice horizontal slices again, but now vertically (`get_vertical_slice(horizontal_slice, config['zoom'])`)
    * The `width_threshold` parameter specified in the script defines how *long* the groups will be. Currently we use a width of 40 tiles.
* create tasks for each group polygon and add to the group dictionary (`create_tasks(xmin, xmax, ymin, ymax, config)`)

<img src="/_static/img/project.png" width="250px"> <img src="/_static/img/horizontally_sliced_groups.png" width="250px"> <img src="/_static/img/vertically_sliced_groups.png" width="250px">

#### How to run
You can run the `create_groups` script like this:
* `python create_groups.py -i=data/project_13505.kml -t=bing -z=18 -p=13505`

Parameters:
* `-i` or `--input_file`: the input file containning the geometry as kml, shp or geojson
* `-t` or `--tileserver`: choose ['bing' (default), 'digital_globe', 'google', 'custom']
* `-z` or `--zoomlevel`: defines the resolution and number of tasks, default(18)
* `-p` or `--project_id`: the id of the respective project
* `-c` or `--custom_tileserver_url`: provide a custom url, if you defined `custom` as tilevserver. Make sure that this url containers `{z}`, `{x}`, `{y}` placeholders.


## Export

The export module gets data from firebase and mysql and saves it as json files. The following files are created:
* `projects.json`: contains all project information as in firebase projects table
* `stats.json`: contains information on total number of users, total distance mapped, total contributions
* `users.json`: contains information on all users as in firebase users table
* `124.json`, `303.json`, ...: contain project results


### Authentification Configuration and Requirements

To properly run the update process you need the following credentials:
* access to firebase
* access to mapswipe mysql database

The default configuration is stored in [auth.py](../cfg/auth.py). You can adapt to your own settings by providing a `config.cfg` file in the same folder as the auth.py script. You can use the [template](../cfg/your_config_file.cfg) for this.


### How to run update

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

### Submodules

#### Export Project Results

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


## Update

The update module updates the progress and number of contributors for MapSwipe projects stored in the firebase projects table.

### Authentification Configuration and Requirements

To properly run the update process you need the following credentials:
* access to firebase
* access to mapswipe mysql database

The default configuration is stored in [auth.py](../cfg/auth.py). You can adapt to your own settings by providing a `config.cfg` file in the same folder as the auth.py script. You can use the [template](../cfg/your_config_file.cfg) for this.

### How to run update

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


### Submodules

#### Update Project Contributors
j
How to run:
* `python update_project_contributors.py`
* `python update_project_contributors.py -p 124 303 5519`

Parameters:
* `-p` or `--projects`: project id as integer. Only projects corresponding to the provided ids will be downloaded and/or updated.


#### Update Project Progress

How to run:
* `python update_project_progress.py`
* `python update_project_progress.py -p 124 303 5519`

Parameters:
* `-p` or `--projects`: project id as integer. Only projects corresponding to the provided ids will be downloaded and/or updated.


## Transfer Results

The transfer results module downloads results from firebase results table and inserts them into the mysql results table. All results that have been inserted successfully will be removed from firebase. Results that have already been imported (*duplicates*) will be removed from firebase.


### Authentification Configuration and Requirements

To properly run the update process you need the following credentials:
* access to firebase
* access to mapswipe mysql database

The default configuration is stored in [auth.py](../cfg/auth.py). You can adapt to your own settings by providing a `config.cfg` file in the same folder as the auth.py script. You can use the [template](../cfg/your_config_file.cfg) for this.


### How to run update

You can run the transfer result script like this:
* `python transfer_results.py`

Parameters:
* `-l` or `--loop`: if this option is set, the import will be looped
* `-m` or `--max_iterations`: the maximum number of imports that should be performed in integer
* `-s` or `--sleep_time`: the time in seconds for which the script will pause in beetween two imports

PM2 Process Manager settings:
* we can use pm2 process manager to loop the script
* a pm2 configuration is provided in `loop_transfer_results.json`
* currently we start the update process every 60 seconds (1 minute)
* you can monitor the process on the server like this:
```
sudo su
pm2 list
tail -100 /data/python-mapswipe-workers/transfer_results_module/transfer_results.log
```


### Test manually

After starting the transfer results script using pm2 process manager you can type `pm2 logs {id}` to get the logs of your specific task. The output in pm2 should look like this:
```
0|loop_tra | 2018-05-25 12:13 +00:00:  
0|loop_tra | ###### ###### ###### ######
0|loop_tra | ###### iteration: 1 ######
0|loop_tra | ###### ###### ###### ######
0|loop_tra | opened connection to firebase
0|loop_tra | downloaded all results from firebase
0|loop_tra | wrote results data to results.json
0|loop_tra | there are 23 results to import
0|loop_tra | dropped raw results table
0|loop_tra | Created new table for raw results
0|loop_tra | copied results information to mysql
0|loop_tra | inserted raw results into results table and updated duplicates count
0|loop_tra | finished deleting results
0|loop_tra | removed "results.json" file
0|loop_tra | import finished and max iterations reached. sleeping now.
```


### Tests using docker

To run tests using docker, simply run the following commnands:
```
cd docker
docker-compose run mapswipe-workers bash -c "make tests"
```
