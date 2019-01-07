# API

> This is very much work in progress. I made this so that we could have something out sooner rather than later. If you are looking to add projects to Mapswipe, please email pete.masters@london.msf.org 

## Intro 

**File size**
Since Mapswipe results are fairly large, we recommend minimizing the amount of requests you make to our API to save bandwidth costs. If we notice that your IP is making excessive use of our resources we will block your IP address. 

**Untouched data**
This is RAW, UNPROCESSED data, meaning that you have to decide what is valid and invalid data. We simply provide users with a way to contribute, it is up to you which users to filter out. We provide the user_id property in results so you can ban users if you find results unacceptable. The user id will not change for a user, ever. In the future we will try to catch cheaters more effectively. 

**Tiles**
We do not publish the tile URLs to avoid abuse at the moment. This may change in the future. If you want, you can always calculate the tile url based on the task x, y, and z, which correspond to tile x, y, and z on Bing. Make sure you ask Bing for your own API key. 

**Large, complex applications**
Please email pim@whitespell.com for a read-only MySQL connection to public data. 


## Endpoints

### List all projects

http://api.mapswipe.org/projects.json 

Each project contains the following key properties:

| key | description |
| --- | --- |
| id | Numeric id of the project |
| lookFor | The project objective (e.g. Houses and Roads) |
| contributors | The amount of people that contributed |
| groupAverage | Average group size in tiles (irrelevant here) |
| image | The image used for the project |
| isFeatured | Whether the project is featured in the app |
| name | Name of the project |
| results | Link to the results file (Note, this can be a very large response, up to 100MB each) |
| progress | Percentage amount of project completion |
| projectDetails | Details of the project |
| state | State of the project (0=not started, 1= on hold, 2=complete, 3=hidden) |

```json
[
  null,
  {
    "contributors": 1517,
    "groupAverage": 221.80340667139816,
    "id": "1",
    "image": "http://wiki.openstreetmap.org/w/images/a/ac/MSF158153_Small.jpg",
    "importKey": "-KMdpOSLV7LttDu2IP-F",
    "isFeatured": true,
    "lookFor": "Houses & Roads",
    "name": "Niger State, Nigeria (part 1)",
    "progress": 122,
    "projectDetails": "Swipe slowly through the satellite imagery and mark anything that looks like it could be a house, village, hut, road or track.\n\nNiger State is an extremely vulnerable area of Nigeria and the data you contribute will help NGOs better deliver services to local people.\n",
    "state": 2,
    "verificationCount": "3",
    "results": "http://api.mapswipe.org/projects/1.json"
  },
  {
    "contributors": 940,
    "groupAverage": 200.58151093439363,
    "id": "14",
    "image": "http://wiki.openstreetmap.org/w/images/a/ac/MSF158153_Small.jpg",
    "importKey": "-KMfQvc8KnPV5SDjj82W",
    "isFeatured": false,
    "lookFor": "Houses & Roads",
    "name": "Map South Kivu (DRCongo) 1",
    "progress": 143,
    "projectDescription": "Swipe slowly through the satellite imagery and mark anything that looks like it could be a house, village, hut, road, or track.\n\nThe people of South Kivu have been experiencing humanitarian crises for decades and the maps will help NGOs better deliver medical care and services in the province.",
    "projectDetails": "Swipe slowly through the satellite imagery and mark anything that looks like it could be a house, village, hut, road, or track.\n\nThe people of South Kivu have been experiencing humanitarian crises for decades and the maps will help NGOs better deliver medical care and services in the province.",
    "state": 2,
    "verificationCount": "3",
    "results": "http://api.mapswipe.org/projects/14.json"
  }
]
```

### Individual results

http://api.mapswipe.org/projects/14.json

Each result set contains the following key properties.

| key | description |
| --- | --- |
| task_id | The task id (z-x-y) |
| user_id | The user id who submitted the contribution. This is useful if you want to filter out certain users. (e.g. if you notice their results are too inaccurate) |
| project_id | The project id of the result |
| timestamp | Timestamp of when the result was submitted |
| wkt | Well known text value of the result, NOTE: This can be null, in earlier versions of Mapswipe we did not log this value. We prefer you calculate the WKT yourself based on the task_x, task_y, and task_z. About 10% of all submissions do not have a wkt, and this will go to 0% on future projects.  |
| task_x | X tile value at zoom level task_z |
| task_y | X tile value at zoom level task_z |
| task_z | Zoom level of the tile |
| result | 1=yes,2=maybe,3=bad imagery |
| duplicates | Don't worry about this for now - internal use to see if users see tiles twice. |

```json
[
  {
    "task_id": "18-136172-124691",
    "user_id": "QOdGtguOjjhSDLiBdKOzFHqmPIv2",
    "project_id": 14,
    "timestamp": 1468833898804,
    "result": 1,
    "wkt": "POLYGON ((7.0037841796875 8.729005290108972 0,7.005157470703125 8.729005290108972 0,7.005157470703125 8.727647903198871 0,7.0037841796875 8.727647903198871 0,7.0037841796875 8.729005290108972 0))",
    "task_x": "136172",
    "task_y": "124691",
    "task_z": "18",
    "duplicates": 0
  },
  {
    "task_id": "18-136172-124692",
    "user_id": "QOdGtguOjjhSDLiBdKOzFHqmPIv2",
    "project_id": 14,
    "timestamp": 1468833898805,
    "result": 1,
    "wkt": "POLYGON ((7.0037841796875 8.727647903198871 0,7.005157470703125 8.727647903198871 0,7.005157470703125 8.726290511352047 0,7.0037841796875 8.726290511352047 0,7.0037841796875 8.727647903198871 0))",
    "task_x": "136172",
    "task_y": "124692",
    "task_z": "18",
    "duplicates": 0
  }
]
```

### Mapswipe stats

http://api.mapswipe.org/stats.json 


### Public User Data

http://api.mapswipe.org/users.json 

This can be useful if you want to filter out cheaters, which are detectable by comparing contributions to the distance - again, this is up to you, we just provide the raw data .

Example user object: `{"00Xo7fMQW4enlk41dVC1b2tEWZG2":{"contributions":399,"distance":10,"username":"ewar"}`
