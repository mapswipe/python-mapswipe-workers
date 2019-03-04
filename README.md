# Python MapSwipe Workers Documentation
[MapSwipe](http://mapswipe.org/) is a mobile app that lets you search satellite imagery to help put the world's most vulnerable people on the map. This repository handles everything related to the backend processing of the app. If you are new to MapSwipe it might be good to have a look at the [FAQs](http://mapswipe.org/faq.html) first.

## Getting Started
The python-mapswipe-workers consist of several python scripts. They do the following things:
* **import**: create new projects for the MapSwipe app, which have been uploaded by project managers from humanitarian organizations
* **transfer results**: make sure that the produced results are stored in a data base
* **update**: generate up-to-date statistics in the app, e.g. progress and number of contributors per project
* **export**: provide access to MapSwipe data in json-format

We created a documentation for this project at [readthedocs](https://mapswipe-workers.readthedocs.io/en/master/).

## Project Types
The MapSwipe backend workers currently support the following project types:

| Name | ID | Description | Screenshot |
| ---- | -- | ----------- | ---------- |
| BuildArea | 1 | A 6 squares layout is used for this project type. By tapping you can classify a tile of satellite imagery as *yes*, *maybe* or *bad_imagery*. Project managers can define which objects to look for, e.g. "buildings". Furthermore, they can specify the tile server of the background satellite imagery, e.g. "bing" or a custom tileserver. | <img src="docs/_static/img/BuildArea_screenshot.png" width="250px"> |

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details

## Authors
* **Benjamin Herfort** - HeiGIT - [Hagellach37](https://github.com/Hagellach37)
* **Marcel Reinmuth** - HeiGIT - [maze2point0](https://github.com/maze2point0)
* **Matthias Schaub** - HeiGIT - [Matthias-Schaub](https://github.com/Matthias-Schaub)

See also the list of [contributors](contributors.md) who participated in this project.

## Acknowledgements
* Humanitarian organizations can't help people if they can't find them.
