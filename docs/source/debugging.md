# Debugging

## Logs - MapSwipe Workers

Where can I find logs?
- `docker logs mapswipe_workers`
- or
- `cat mapswipe-data/mapswipe_workers.log`

Logs are written to directly to the terminal (stdout). The easiest way is therefore is to run `docker logs mapswipe_workers` to see the logs.

Logs are also writing to file inside the Docker container (`~/.local/share/mapswipe_workers/mapswipe_workers.log`). The parent directory of the file is the data directory of MapSwipe Workers. This directory is mounted (as a Docker volume) locally to disk (`mapswipe-data/`). Logs can therefore be accessed as text file as well: `cat mapswipe-data/mapswipe_workers.log`

## Logs - Django web server.
- `docker compose logs django`
- or
- `cat django-data/django.log`

## Common Errors

*Docker containers are always restarting:* Take a look at the docker logs (eg. `docker logs container_name`). If you get an `Unable to load configuration file at ./cfg/config.cfg. Exiting.` due to `PermissionError: [Errno 13] Permission denied: './config/configuration.cfg'` error message, you probably have SELinux on your system enabled. If so you have to configure (change mount option of volumes) your docker-compose file. Please read the documentation provided by Docker regarding this configuration (https://docs.docker.com/storage/bind-mounts/ Chapter: "Configure the selinux label").


## Useful Docker Commands

- `docker ps -a`: list all containers and check status
- `docker image ls`: list all docker images
- `docker exec -it mapswipe_workers bash `: open shell in a running container
- `docker exec -t mapswipe_workers tail -100 /var/log/mapswipe_workers/mapwipe_workers.log`: show last 100 lines of the log file
- `docker stats`: show memory usage, CPU consumption for all running containers
- `docker system prune --all`: clean up any resources — images, containers, volumes, and networks — that are dangling (not associated with a container)

