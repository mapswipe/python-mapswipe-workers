# Testing

## Test Setup

- Install GDAL
- Setup virtual environment with system-site-packages enabled
    - `python3 venv --system-site-packages venv`
    - system site packages is necessary to ensure that GDAL works in virtual environment
- Activate virtual environment
    - `source venv/bin/activate`
- Install mapswipe_workers
    - `pip install -e .`
    - `-e` = `--editable` 
- Setup and install mapswipe_workers as descriped in [setup.md](setup.md).
    - You only need to start the Postgres Container
    - You have to change the `host` name of postgres in your configuration file to `localhost`
- Run tests
