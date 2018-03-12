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


## Tests using docker
To run tests using docker, simply run the following commnands:
```
cd docker
docker-compose run mapswipe-workers bash -c "make tests"
```
