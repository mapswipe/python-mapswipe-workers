# Command Line Interface

THIS DOCUMENT IS OUTDATED: Please use the `--help` flag of the CLI.

---

This document describes how to use the command line interface of MapSwipe Worker.

In our current deployment setup the commands of the MapSwipe Workers CLI are hard-coded in the Docker-Compose File.

You can run these commands also using docker-compose:

```
docker-compose run mapswipe_workers mapswipe_workers --help
```


```
Usage: mapswipe_workers [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --version      Show the version and exit.
  --help         Show this message and exit.

Commands:
  create-projects
  create-tutorial
  firebase-to-postgres
  generate-stats
  run
  user-management
```


## Create projects from submitted project drafts

```
Usage: mapswipe_workers create-projects [OPTIONS]

Options:
  -s, --schedule [m|h|d]  Will create projects every 10 minutes (m), every
                          hour (h) or every day (d).
  --help                  Show this message and exit.
```


## Transfer data from Firebase to Postgres

```
Usage: mapswipe_workers firebase-to-postgres [OPTIONS]

Options:
  -s, --schedule [m|h|d]  Will update and transfer relevant data (i.a. users
                          and results) from Firebase into Postgres every 10
                          minutes (m), every hour (h) or every day (d).
  --help                  Show this message and exit.
```


## Generate Statistics

```
Usage: mapswipe_workers generate-stats [OPTIONS]

Options:
  -s, --schedule [m|h|d]  Generate stats every 10 minutes (m), every hour (h)
                          or every day (d).
  --project_id_list TEXT  provide project id strings as a list stats will be
                          generated only for these projects.
                          Use it like '["project_a", "project_b"]'
  --help                  Show this message and exit.
```

## Generate Statistics for all projects

Ideally you run this using a separate docker container. e.g. like this:

```
docker-compose run mapswipe_workers mapswipe_workers generate-stats-all-projects
```

```
Usage: mapswipe_workers generate-stats-all-projects [OPTIONS]

Options:
  -s, --schedule [m|h|d]  Generate stats every 10 minutes (m), every hour (h)
                          or every day (d).
  --help                  Show this message and exit.
```

## User Management

```
Usage: mapswipe_workers user-management [OPTIONS]

Options:
  --email TEXT       The email of the MapSwipe user.  [required]
  --manager BOOLEAN  Set option to grant or remove project manager
                     credentials. Use true to grant credentials. Use false to
                     remove credentials.
  --help             Show this message and exit.
```


## Create Tutorial from json file (e.g. provided in sample data)

```
Usage: mapswipe_workers create-tutorial [OPTIONS]

Options:
  --input_file TEXT  The json file with your tutorial information.  [required]
  --help             Show this message and exit.

```
