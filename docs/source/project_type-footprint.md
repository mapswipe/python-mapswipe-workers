# Footprint

## Import structure

```json
{
  "inputGeometries" : "https://heibox.uni-heidelberg.de/f/7a61e549b6/?dl=1",
  "project" : {
    "image" : "http://www.fragosus.com/test/Javita.jpg",
    "lookFor" : "Buildings",
    "name" : "Mapping to end FGM in North Monduli",
    "projectDetails" : "Swipe slowly through the satellite imagery and mark anything that looks like it could be a building or village. This area has high levels of girls being subjected to FGM and child marriage.",
    "verificationCount" : "3"
  },
  "projectType" : 2,
  "tileServer" : "bing"
}
```

The `tileserver` attribute can have the following values: `bing`, `custom`. If a custom tileserver is chosen, you need to provide a `custom_tileserver_url` attribute which links to a TMS using x, y, z placeholders.

Imports which have been imported successfully will have a `complete` attribute set to `true`.


## Project structure

```json
{
  "contributors" : 0,
  "groupAverage" : 0,
  "id" : 13564,
  "image" : "http://www.fragosus.com/test/Javita.jpg",
  "importKey" : "-LNOgRd0szBM2HJBX27B",
  "info" : {
    "api_key" : "your_bing_api_key",
    "group_size" : 50,
    "input_geometries_file" : "data/valid_geometries_13564.geojson",
    "tileserver" : "bing"
  },
  "isFeatured" : false,
  "lookFor" : "Buildings",
  "name" : "Mapping to end FGM in North Monduli",
  "progress" : 0,
  "projectDetails" : "Swipe slowly through the satellite imagery and mark anything that looks like it could be a building or village. This area has high levels of girls being subjected to FGM and child marriage.",
  "projectType" : 2,
  "state" : 3,
  "verificationCount" : 3
}
```


## Group structure

```
{
  "completedCount" : 0,
  "count" : 50,
  "id" : 100,
  "neededCount" : 3,
  "project_id" : 13564,
  "tasks" : {...}
}

```


## Task structure

```json
{
  "feature_id" : 0,
  "geojson" : {
    "coordinates" : [ [ [ 5.15910196973, 13.48686869581 ], [ 5.15937974751, 13.48686869581 ], [ 5.15937974751, 13.48742425137 ], [ 5.15910196973, 13.48742425137 ], [ 5.15910196973, 13.48686869581 ] ] ],
    "type" : "Polygon"
  },
  "id" : "13564_100_0",
  "project_id" : 13564
}
```

## Result Structure
```
{"OzDyJJ8su8TQtctYVIg9w5tplaX2":
  {"data":
    {"device":"6a39e920622c4fbb",
     "id":"13555_105_298",
     "item":"Buildings",
     "projectId":13555,
     "result":1,
     "timestamp":1544613097198,
     "user":"OzDyJJ8su8TQtctYVIg9w5tplaX2"
     }
  }
}
```