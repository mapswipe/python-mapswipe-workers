# Debugging

## Logs - MapSwipe Workers

Where can I find logs?

Logs are written to directly to console and also to `/var/log/mapswipe_workers.log`:

- `docker exec -t mapswipe_workers cat /var/log/mapswipe_workers/mapswipe_workers.log` (if container is running)
- `docker logs container_name` (also if container is not running)


## Common Errors

*Docker containers are always restarting:* Take a look at the docker logs (eg. `docker logs container_name`). If you get an `Unable to load configuration file at ./cfg/config.cfg. Exiting.` due to `PermissionError: [Errno 13] Permission denied: './config/configuration.cfg'` error message, you probably have SELinux on your system enabled. If so you have to configure (change mount option of volumes) your docker-compose file. Please read the documentation provided by Docker regarding this configuration (https://docs.docker.com/storage/bind-mounts/ Chapter: "Configure the selinux label").


## Useful Docker Commands

- `docker ps -a`: list all containers and check status
- `docker image ls`: list all docker images
- `docker exec -it mapswipe_workers bash `: open shell in a running container
- `docker exec -t mapswipe_workers tail -100 /var/log/mapswipe_workers/mapwipe_workers.log`: show last 100 lines of the log file
- `docker stats`: show memory usage, CPU consumption for all running containers
- `docker system prune --all`: clean up any resources — images, containers, volumes, and networks — that are dangling (not associated with a container)

