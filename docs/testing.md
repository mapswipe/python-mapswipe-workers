# Testing

## Test Setup

- Install GDAL
- Setup virtual environment with system-site-packages enabled
    - `python3 -m venv --system-site-packages venv`
- Activate virtual environment
    - `source venv/bin/activate`
- Install mapswipe_workers
    - `pip install -e .`
- Setup and install mapswipe_workers as descriped in [setup.md](setup.md).
    - You only need to start the Postgres Container
    - You have to change the `host` name of postgres in your configuration file to `localhost`
- Run tests


## Test order

1. test_initialize.py
2. test_import.py
3. test_mock_results.py
4. test_transfer_results.py
5. test_update.py
6. test_export.py


## Debugging

Directories (eg. data, postgres_data) created by running Docker Containers are probably not in your ownership. Running test scripts as a user will therefor fail to access and get permissions for those directories. If so change permissions for those directories using `sudo chmod a+rw data/`.
