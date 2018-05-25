# Transfer Results Module Documentation

The transfer results module downloads results from firebase results table and inserts them into the mysql results table. All results that have been inserted successfully will be removed from firebase. Results that have already been imported (*duplicates*) will be removed from firebase.

## Authentification Configuration and Requirements
To properly run the update process you need the following credentials:
* access to firebase
* access to mapswipe mysql database

The default configuration is stored in [auth.py](../cfg/auth.py). You can adapt to your own settings by providing a `config.cfg` file in the same folder as the auth.py script. You can use the [template](../cfg/your_config_file.cfg) for this.

## How to run update
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

## Test manually
After starting the transfer results script using pm2 process manager you can type `pm2 logs {id}` to get the logs of your specific task. The ouput in pm2 should look like this:
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

## Tests using docker
To run tests using docker, simply run the following commnands:
```
cd docker
docker-compose run mapswipe-workers bash -c "make tests"
```
