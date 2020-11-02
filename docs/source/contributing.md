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

This project uses [black](https://github.com/psf/black), [flake8](https://gitlab.com/pycqa/flake8) and [isort](https://github.com/PyCQA/isort) to achive a constisted style across the project.
The configuration of flake8 and isort is stored in `setup.cfg`.

Use [pre-commit](https://pre-commit.com/) to run `black` and `flake8` prior to any git commit. `pre-commit`, `black` and `flake8` should already be installed in your virtual environment since they are listed in `requirements.txt`. To setup pre-commit simply run:

```
pre-commit install
```

From now on `black`, `flake8` and `isort` should run automatically whenever `git commit` is executed.

When running those tools manually please make sure the right version is used. The version can be looked up in `.pre-commit-config.yaml`.
To update to newer version please make sure to change version numbers in `.pre-commit-config.yaml`, `.travis.yml` and `requirements.txt`.


### Tips

Ignore a hook: `SKIP=flake8 git commit -m "foo"`
Mark in code that flake8 should ignore the line: `print()  # noqa`

