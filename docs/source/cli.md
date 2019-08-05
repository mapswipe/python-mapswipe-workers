# Command Line Interface

```
Usage: mapswipe_workers [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --version      Show the version and exit.
  --help         Show this message and exit.

Commands:
  create-projects
  firebase-to-postgres
  generate-stats
  run
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
  -s, --schedule [m|h|d]  Will generate stats every 10 minutes (m), every hour
                          (h) or every day (d).
  --help                  Show this message and exit.
```
