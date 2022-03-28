# Change Detection

## Project Draft

The Change detection project type is initialized in the same way as the standard buildArea project.

Project Draft example for a Change Detection project:
```json
{
  "createdBy": "Sample Manager",
  "geometry": {"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-175.21785736083984,-21.122295110595505],[-175.2367401123047,-21.148873980682744],[-175.21339416503906,-21.152716314425852],[-175.19931793212888,-21.15239612375494],[-175.19588470458984,-21.147913381670975],[-175.1931381225586,-21.136385707660683],[-175.1934814453125,-21.129660817021904],[-175.21785736083984,-21.122295110595505]]]}}]},
  "image": "http://www.redcrosseth.org/media/k2/items/cache/5a05a447acfdf6fcc40548cc4c1cea8d_L.jpg",
  "lookFor": "DESTROYED BUILDINGS",
  "name": "Change Detection Sample Project",
  "projectDetails": "This project uses Bing as the tile server and zoom level 18 for the before image. For after we use imagery from open aerial map.",
  "verificationNumber": 3,
  "groupSize": 15,
  "projectType": 3,
  "tileServerA": {
    "name": "bing",
    "apiKeyRequired": true,
    "caption": "Before",
    "credits": "© 2019 Microsoft Corporation, Earthstar Geographics SIO"
  },
  "tileServerB": {
    "name": "custom",
    "url": "https://tiles.openaerialmap.org/5b3541802b6a08001185f8b1/0/5b3541802b6a08001185f8b2/{z}/{x}/{y}.png",
    "apiKeyRequired": false,
    "apiKey": "",
    "caption": "After",
    "date": "2018-02-21",
    "credits": "© OpenAerialMap"
  }
}
```
Examples of other initialization options can be found in the mapswipe-backend repository at mapswipe_workers/tests/integration/fixtures/change_detection/project_drafts.json.

## Project structure

Project Structure example for a project which was created via HOT Tasking Manager Project ID.
```json
{
  "contributorCount" : 0,
  "created" : "2021-12-23T14:14:52.179930Z",
  "createdBy" : "X0zTSyvY0khDfRwc99aQfIjTEPK2",
  "groupMaxSize" : 0,
  "groupSize" : 25,
  "image" : "https://firebasestorage.googleapis.com/v0/b/dev-mapswipe.appspot.com/o/projectImages%2FEQ%2BEarthquake.png?alt=media&token=6e82ba52-8adb-4214-8f81-4b7030c00946",
  "isFeatured" : false,
  "lookFor" : "damaged buildings",
  "name" : "Earthquake - Experimental Damage Assessment - Les Cayes (Haiti) (1)\nSimon BA",
  "progress" : 0,
  "projectDetails" : "In attempt to provide a rapid damage assessment for the 7.2 magnitude earthquake on August 14, please slowly compare the images to determine if damage is visible in the post-event scene. This methodology is still being tested and should not replace traditional damage assessment methods. Imagery is provided through [Maxar's Open Data Programm](https://www.maxar.com/open-data) and hosted by [MapBox](https://www.mapbox.com/).",
  "projectId" : "-Mrbd5ArF4lb_GoYG2I5",
  "projectNumber" : "1",
  "projectRegion" : "Les Cayes (Haiti)",
  "projectTopic" : "Earthquake - Experimental Damage Assessment",
  "projectType" : 3,
  "requestingOrganisation" : "Simon BA",
  "requiredResults" : 3636,
  "resultCount" : 0,
  "status" : "inactive",
  "tileServer" : {
    "apiKey" : "f57b8754-0d70-4439-bdb4-641beea5c2ec",
    "credits" : "© 2019 Maxar",
    "name" : "maxar_premium",
    "url" : "https://services.digitalglobe.com/earthservice/tmsaccess/tms/1.0.0/DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/{z}/{x}/{y}.jpg?connectId={key}"
  },
  "tileServerB" : {
    "credits" : "© Maxar, MapBox",
    "name" : "custom",
    "url" : "https://api.mapbox.com/v4/mapboxsatellite.haiti-post-2021/{z}/{x}/{y}.webp?sku=101Fw3jtBuWI5&access_token=pk.eyJ1IjoibWFwYm94c2F0ZWxsaXRlIiwiYSI6ImNqZWZ0MHg0djFqZWoyeG9kN3ZiMmkyd3cifQ.y2HNjGo7FcKQ7psI_BfGqQ"
  },
  "tutorialId" : "tutorial_-MhJtd9ePFOw8Vs6xwZ2",
  "verificationNumber" : 3,
  "zoomLevel" : 19
}
```


## Group structure

| Parameter    | Description                                                                                                |
|--------------|------------------------------------------------------------------------------------------------------------|
| **Geometry** | The Change Detection groups save the bounding box coordinates in fields labeled xMax, xMin, yMax and yMin. |

## Task structure


| Parameter                           | Description                                                                                                                                                                                                                                                                                                                                                                            |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Project Type Specific Information* |                                                                                                                                                                                                                                                                                                                                                                                        |
| **Task X**                          | The x coordinate characterises the longitudinal position of the tile in the overall tile map system taken the zoom level into account. The x coordinates increase from west to east starting at a longitude of -180 degrees.                                                                                                                                                           |
| **Task Y**                          | The y coordinate characterises the latitudinal position of the tile in the overall tile map system taken the zoom level into account. The latitude is clipped to range from circa -85 to 85 degrees. The y coordinates increase from north to south starting at a latitude of around 85 degrees.                                                                                       |
| **Geometry**                        | Each task has a polygon geometry, which can be generated by its x, y and z coordinates. At the equator the task geometry is a square with an edge length of around 150 metres covering circa 0.0225 square kilometres. Due to the web Mercator projector the task geometry will be clinched with increasing distance to the equator. At the same time the area per task will decrease. |
| **URL**                             | Image for the tile at timestamp A. The tile URL points to the specific tile image described by the x, y, and z coordinates.                                                                                                                                                                                                                                                            |
| **URL 2**                           | Image for the tile after timestamp A. The tile URL points to the specific tile image described by the x, y, and z coordinates.                                                                                                                                                                                                                                                         |


## Result Structure
```json
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
