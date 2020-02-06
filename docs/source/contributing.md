# Contributing

This document describes how to setup Python MapSwipe Workers locally without using the provided Dockerfile for development purposes.


## Feature Branch

To contribute to the MapSwipe back-end please create dedicated feature branches based on the `dev` branch:

```bash
git checkout dev
git checkout -b featureA
# Hack away ...
git commit -am 'Describe changes.'
git push -u origin featureA
# Create a Pull Request from feature branch into the dev branch on GitHub.
```

> Note: If a bug in production (master branch) needs fixing before a new versions of MapSwipe Workers gets released (merging dev into master branch), a hotfix branch should be created. In the hotfix branch the bug should be fixed and then merged with the master branch (and also dev).


## Style Guide

This project uses [black](https://github.com/psf/black) and [flake8](https://gitlab.com/pycqa/flake8) to achieve a unified style.

Use [pre-commit](https://pre-commit.com/) to run `black` and `flake8` prior to any git commit. `pre-commit`, `black` and `flake8` should already be installed in your virtual environment since they are listed in `requirements.txt`. To setup pre-commit simply run:

```
pre-commit install
```

From now on `black` and `flake8` should run automatically whenever `git commit` is executed.
