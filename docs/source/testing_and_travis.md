# Testing and Travis

## Tests
* run tests locally during development

```
python -m unittest discover --verbose --start-directory mapswipe_workers/tests/unittests/
python -m unittest discover --verbose --start-directory mapswipe_workers/tests/integration/
```


## Travis
* set environment variables in travis
* travis then sets up the docker containers
* test are run inside the mapswipe_workers docker container

```
docker-compose run mapswipe_workers python -m unittest discover --verbose --start-directory tests/unittests/
docker-compose run mapswipe_workers python -m unittest discover --verbose --start-directory tests/integration/
```