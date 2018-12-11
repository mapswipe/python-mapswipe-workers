# Enable new project types
Currently MapSwipe handles only one type of mapping project. The one with the six squares working tiles as an input. Users tap several times to indicate the presence of buildings. However, there might be more to be mapped. Think about a building by building validation of footprint geometries or even detectiing change on pairs of satellite imagery.

To address such new mapping tasks we need to enable that projects can have different tpyes. Each project type will refer to a specific backend workflow (import, export) and will use a different map view in the app. We might also want to show different instructions for each project types and have distinct tutorials.

In this document we will try to document what we need to consider when shifting to multiple project types.

## Projects
projects need a “type”, e,g, 1, 2, 3 or “binary”, “validation”
this needs to be set during the import (add to html importer)
the main project view should show the project types
when starting to map we should check the project type and the
 corresponding map view needs to be displayed (each project type has its own mapping view)
project type will also be considered during the import module, task creation etc.

This is how projects are currently looking like:
```
{
  "contributors" : 0,
  "groupAverage" : 0.0,
  "id" : "1002",
  "image" : "http://www.redcrosseth.org/media/k2/items/cache/5a05a447acfdf6fcc40548cc4c1cea8d_L.jpg",
  "importKey" : "-LK7IpMFNJ7mwe2IQych",
  "isFeatured" : false,
  "lookFor" : "BUILDINGS",
  "name" : "Map vulnerable communities in Ethiopia 4",
  "progress" : 0,
  "projectDetails" : "Ethiopia has a population of over 102 million, yet many people live in remote and rural locations. These communities are vulnerable to flooding, droughts and other extreme climate related events. The Red Cross, with the support of the IKEA Foundation is asking you to help map and locate these rural communities, allowing the Red Cross help prepare them for any pending disasters. Please swipe slowly through the satellite imagery and tap anything that looks like it could be a building or village.",
  "state" : 3,
  "tileserver" : "bing",
  "type" : 1,
  "verificationCount" : "3",
  "zoom" : 18
}
```

And here is a proposed project structure to allow multiple project types:
```
{
  "contributors" : 0,
  "id" : "1002",
  "image" : "http://www.redcrosseth.org/media/k2/items/cache/5a05a447acfdf6fcc40548cc4c1cea8d_L.jpg",
  "importKey" : "-LK7IpMFNJ7mwe2IQych",
  "isFeatured" : false,
  "lookFor" : "BUILDINGS",
  "name" : "Map vulnerable communities in Ethiopia 4",
  "progress" : 0,
  "projectDetails" : "Ethiopia has a population of over 102 million, yet many people live in remote and rural locations. These communities are vulnerable to flooding, droughts and other extreme climate related events. The Red Cross, with the support of the IKEA Foundation is asking you to help map and locate these rural communities, allowing the Red Cross help prepare them for any pending disasters. Please swipe slowly through the satellite imagery and tap anything that looks like it could be a building or village.",
  "state" : 3,
  "type" : 1,
  "verificationCount" : "3",
  "settings": {
    "tileserver" : "bing",
    "zoom" : 18"
    }
}
```
Each project will have basic information describing the content: `id`, `name`, `projectDetails`, `lookFor`, `image`, `importKey` and a new `type` attribute.

Furthermore, there are some attributes related to stats and displaying the project in the app: `isFeatured`, `state`, `contributors` and `progress`.

Finally, a new `settings` attribute is proposed. This attribute will be different for each project type.

For `type a` (built_area_type) it would look like this:
```
"settings": {
  "tileserver" : "bing",
  "zoom" : 18",
  "extent": "./data/project_xy.kml"
}
```

For `type b` (building_footprint_validation) it would look like this:
```
"settings": {
  "tileserver" : "digital_globe",
  "input_geometry": "./data/project_xy_buildings.geojson"
}
```
You could add new types of projects and would only need to adjust `the settings` part of a project.

## Groups
Groups are uploaded to firebase and contain `tasks`. Groups will be displayed in the mapping view in the app. For different project types, groups will have somehow different format.

This is how groups are currently looking like:#
```
{
  "completedCount" : 0,
  "count" : 114,
  "distributedCount" : 0,
  "id" : 1878,
  "projectId" : "9",
  "reportCount" : 0,
  "tasks" : {...},
  "xMax" : "160176",
  "xMin" : "160139",
  "yMax" : "127033",
  "yMin" : "127031",
  "zoomLevel" : 18
```

And here is a proposed group structure to allow multiple project types:
```
{
  "completedCount" : 0,
  "count" : 114,
  "neededCount" : 0,
  "id" : 1878,
  "projectId" : "9",
  "tasks" : {...},
  "type": 1,
  "users": ["user_a", "user_b", ... ,"user_x"]
```

Some of the attributes of the old structure have not been used: `distributedCount`, `reportCount`.

Furthermore, I'm not sure how `zoomLevel`, `xMax`, `xMin`, `yMax`, `yMin` are used by the app. This information should also be included in the `tasks`.

 Adding a `neededCount` attribute will allow us to set a dynamic number of users needed for each group. This would help us in addressing low quality, by adding more users for these specific groups.

 Adding a `users` attribute will help us to distribute each groups only to each user. We are currently not sure if sometimes users work on a group twice.

 Finally, there is a `type` attribute. I'm not sure if that's actually needed. There is nothing type specific for groups at the moment, except the structure of the `tasks`.

## Tasks
Tasks are the most basic structure in our crowdsourcing workfflow. They have all the information needed to display the task to the user in the app.

Currently, tasks look like this:
```
"18-160175-127033" : {
  "id" : "18-160175-127033",
  "projectId" : "9",
  "taskX" : "160175",
  "taskY" : "127033",
  "taskZ" : "18",
  "url" : "http://t0.tiles.virtualearth.net/tiles/a122333000110323113.jpeg?g=854&mkt=en-US&token=AopsdXjtTu-IwNoCTiZBtgRJ1g7yPkzAi65nXplc-eLJwZHYlAIf2yuSY_Kjg3Wn",
  "wkt" : ""
}
```

And here is a proposed task structure to allow multiple project types:
```
"18-160175-127033" : {
  "id" : "18-160175-127033",
  "projectId" : "9",
  "type": 1,
  "info": {
    "taskX" : "160175",
    "taskY" : "127033",
    "taskZ" : "18",
    "url" : "http://t0.tiles.virtualearth.net/tiles/a122333000110323113.jpeg?g=854&mkt=en-US&token=AopsdXjtTu-IwNoCTiZBtgRJ1g7yPkzAi65nXplc-eLJwZHYlAIf2yuSY_Kjg3Wn",
    "wkt" : ""
  }
}
```
The most basic information per task are `id` (composed of some cool structure, which might be different regarding different projects), `projectId` and the `type` of a project.

All other information will go into a new `info` attribute. This will look differently concerning the type of the project. The `info` attribute should contain all information needed for displaying the task in the app.



## Results



## Import Workflow
check for new imports and check the type of the project/import
make sure that this does not conflict with our current import workflow, enable that type=”1” refers to the current import workflow
create new import and create new groups for different project type
let’s stick to the idea of groups
what is the input needed for a building by building project

## Data Model
the current data model is based on tasks with an ID generated using the TMS schema
new project types might require a different data model
a data model with custom input geometries (e.g. building footprints) might need a different data model

