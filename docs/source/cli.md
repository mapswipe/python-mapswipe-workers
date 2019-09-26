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
