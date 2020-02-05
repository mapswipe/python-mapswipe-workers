# MapSwipe Back-End

[MapSwipe](http://mapswipe.org/) is a mobile app that lets you search satellite imagery to help put the world's most vulnerable people on the map. If you are new to MapSwipe it might be good to have a look at the [FAQs](http://mapswipe.org/faq.html) first.

The MapSwipe Back-End consists of a number of components:

1. Firebase Project
2. MapSwipe Workers
4. Postgres Database
3. Manager Dashboard
5. API

Please refer to the documentation for more information: https://mapswipe-workers.readthedocs.io/


## Ressources

- MapSwipe Back-End: https://github.com/mapswipe/python-mapswipe-workers
- MapSwipe App https://github.com/mapswipe/mapswipe
- MapSwipe Website: https://mapswipe.org
- MapSwipe OSM-Wiki: https://wiki.openstreetmap.org/wiki/MapSwipe


## Contributing Guidelines

### Feature Branch

To contribute to the MapSwipe back-end please create dedicated feature branches based on the `dev` branch. After the changes create a Pull Request of the `feature` branch into the `dev` branch on GitHub:

```bash
git checkout dev
git checkout -b featureA
# Hack away ...
git commit -am 'Describe changes.'
git push -u origin featureA
# Create a Pull Request from feature branch into the dev branch on GitHub.
```

> Note: If a bug in production (master branch) needs fixing before a new versions of MapSwipe Workers gets released (merging dev into master branch), a hotfix branch should be created. In the hotfix branch the bug should be fixed and then merged with the master branch (and also dev).


### Style Guide

This project uses [black](https://github.com/psf/black) and [flake8](https://gitlab.com/pycqa/flake8) to achieve a unified style.

Use [pre-commit](https://pre-commit.com/) to run `black` and `flake8` prior to any git commit. `pre-commit`, `black` and `flake8` should already be installed in your virtual environment since they are listed in `requirements.txt`. To setup pre-commit simply run:

```
pre-commit install
```

From now on `black` and `flake8` should run automatically whenever `git commit` is executed.


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details


## Authors

* **Benjamin Herfort** - HeiGIT - [Hagellach37](https://github.com/Hagellach37)
* **Marcel Reinmuth** - HeiGIT - [maze2point0](https://github.com/maze2point0)
* **Matthias Schaub** - HeiGIT - [Matthias-Schaub](https://github.com/Matthias-Schaub)

See also the list of [contributors](contributors.md) who participated in this project.


## Acknowledgements

* Humanitarian organizations can't help people if they can't find them.
