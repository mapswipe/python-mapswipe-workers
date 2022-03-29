# Command Line Interface

The Mapswipe Backend provides a Command Line Interface(CLI) with which the users can interact with the program.
They can be used for example to create projects, which were uploaded to the [manager-dashboard](for_mapswipe_managers.html),
or to export statistics on the finished projects. To get a comprehensible lists of the available commands use the ```--help``` flag.

```mapswipe_workers --help``` would get you all possible commands, while e.g. ```mapswipe_workers archive --help``` would get you additional information on how to use that command.

In our current deployment setup the commands of the MapSwipe Workers CLI are hard-coded in the Docker-Compose File.

You can run these commands also using docker-compose:

```
docker-compose run mapswipe_workers mapswipe_workers --help
```
