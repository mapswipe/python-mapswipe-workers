# Contributing


## Clone from GitHub

```bash
git clone https://github.com/mapswipe/python-mapswipe-workers.git
cd python-mapswipe-workers
git checkout dev
```


## Install MapSwipe Workers

Create a Python virtual environment and activate it. Install MapSwipe Workers using pip:

```bash
python -m venv venv
source venv/bin/activate
pip install --editable .
```


## Feature Branch

To contribute to the MapSwipe back-end please create dedicated feature branches from dev:

```bash
git checkout dev
git checkout -b featureA
git commit -am 'add new project type'
git push -u origin featureA
git request-pull origin/dev featureA
```

> Note: If a bug in production (master branch) needs fixing before a new versions of MapSwipe Workers gets released (merging dev into master branch), a hotfix branch should be created. In the hotfix branch the bug should be fixed and then merged back with master and also dev.


## Style Guide

This project uses [black](https://github.com/psf/black) and [flake8](https://gitlab.com/pycqa/flake8) to achieve a unified style.

Use [pre-commit](https://pre-commit.com/) to run `black` and `flake8` prior to any git commit. `pre-commit`, `black` and `flake8` should already be installed in your virtual environment since they are listed in `requirements.txt`. To setup pre-commit simply run:

```
pre-commit install
```

From now on `black` and `flake8` should run automatically whenever `git commit` is executed.
