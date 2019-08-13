# Build Area

![Build Area](_static/img/data_structure-firebase-1.svg)

| Name | ID | Description | Screenshot |
| ---- | -- | ----------- | ---------- |
| BuildArea | 1 | A 6 squares layout is used for this project type. By tapping you can classify a tile of satellite imagery as *yes*, *maybe* or *bad_imagery*. Project managers can define which objects to look for, e.g. "buildings". Furthermore, they can specify the tile server of the background satellite imagery, e.g. "bing" or a custom tile server. | <img src="_static/img/BuildArea_screenshot.png" width="250px"> |


## Data Model
The MapSwipe crowdsourcing workflow is designed following an approach already presented by [Albuquerque et al. (2016)](http://www.mdpi.com/2072-4292/8/10/859). Five concepts are important in the following:
* project drafts
* projects
* groups
* tasks
* results.

| <img src="_static/img/mapswipe_data_model.png">

As a project manager you have to care about the **Project Drafts** only. The information you provide through the **Manager Dashboard** will be used to set up your project. You should provide the following information.

### Project Drafts
The project drafts contain all information needed to set up your project. Only MapSwipe user accounts with dedicated project manager role can create projects. Make sure to get the rights before submitting project drafts.

| Parameter | Description |
| --- | --- |
| _Basic Project Information_ |
| **Name** |  The name of your project (25 chars max) |
| **Look For** | What should the users look for (e.g. buildings, cars, trees)? (15 chars max). |
| **Project Type** | Is `1` for all Build Area projects. |
| **Direct Image Link** | An url to an image. Make sure you have the rights to use this image. It should end with .jpg or .png. |
| **Project Details** |  The description for your project. (3-5 sentences).  |
| **Verification Number** | How many people do you want to see every tile before you consider it finished? (default is 3 - more is recommended for harder tasks, but this will also make project take longer) |
| **Group Size** | How big should a mapping session be? Group size refers to the number of tasks per mapping session. |
| _Project Type Specific Information_ |
| **Zoom Level** | We use the Tile Map Service zoom levels. Please check for your area which zoom level is available. For example, Bing imagery is available at zoomlevel 18 for most regions. If you use a custom tile server you may be able to use even higher zoom levels. |
| **KML file Content** | The content of a KML file. Make sure that you provide a single polygon geometry. |
| **Tile Server Name** | Select the tile server providing satellite imagery tiles for your project. Make sure you have permission. You can choose: `Bing`, `Digital Globe`, `Sinergise`,  `Custom` |
| **Custom Tile Server URL** (optional) | A custom tile server URL that uses {z}, {x} and {y} as placeholders and that already includes the api key. This is only needed if you choose `Custom` as the _Tile Server Name_ |
| **WMTS Layer Name** (optional) | Enter the name of the layer of the Web Map Tile Service (WMTS). This is only needed if you choose `Sinergise` as the _Tile Server Name_. |
| **API Key required** (optional) | Do you need an api key for the imagery? |
| **API Key** (optional)| Insert the api key if required. |


### Projects
Projects get created from _Project Drafts_ by the Mapswipe workers. The workers extend the information by the following parameters.


### Tasks
To create a new mapping task, the overall project extent is split up into many single tasks. Tasks are the smallest unit in the MapSwipe data model. They are derived from the area of interest by gridding it into many small equal-sized rectangular polygons. Each task corresponds to a specific tile coordinate from a tile map service (TMS) using a web Mercator projection as its geographical reference system. Therefore, each task is characterized by a geometry and its tile coordinates, which describe its x, y and z position. For the projects analysed in this project, the tiles for all tasks are generated at zoom level 18. Taking the latitude of each task location into account the satellite imagery has a maximum spatial resolution of ~ 0.6 meter at the equator.

| Parameter | Description |
| --- | --- |
| **Id** | Each task can be identified by its Id. The Id is a composition of its position in the corresponding tile map system, which can be described by the x, y and z coordinates. |
| **Tile Z** | The z coordinate of the tile defines the zoom level. Greater values for z will correspond to higher spatial resolution of the corresponding image. For most regions Bing provides images up to zoom level 18. For aerial imagery or images captured by UAVs even higher z values are valid. |
| **Tile X**| The x coordinate characterises the longitudinal position of the tile in the overall tile map system taken the zoom level into account. The x coordinates increase from west to east starting at a longitude of -180 degrees. |
| **Tile Y** | The y coordinate characterises the latitudinal position of the tile in the overall tile map system taken the zoom level into account. The latitude is clipped to range from circa -85 to 85 degrees. The y coordinates increase from north to south starting at a latitude of around 85 degrees. |
| **Geometry** | Each task has a polygon geometry, which can be generated by its x, y and z coordinates. At the equator the task geometry is a square with an edge length of around 150 metres covering circa 0.0225 square kilometres. Due to the web Mercator projector the task geometry will be clinched with increasing distance to the equator. At the same time the area per task will decrease. |
| **Tile URL** | The tile URL points to the specific tile image described by the x, y, and z coordinates. Usually, the image has a resolution of 256 x 256 pixels. However, some providers also generate image tiles with higher resolution (e.g. 512 x 512 pixels). |

### Groups

Single MapSwipe projects can contain up to several hundred thousand tasks. This can pose a challenge to fast and performant communication between clients and server if many volunteers contribute data at the same time. Therefore, groups have been introduced to reduce the amount of client requests on the backend server. Groups consists of several tasks, that will be shown to the user in one mapping session. The grouping algorithm uses the extent of a project as an input and generates chunks of tasks lying next to each other. Each group has a height of three tasks and a width of approximately 40 tasks.

| Parameter | Description |
| --- | --- |
| **Id** | Each group can be identified by its Id. |
| **Tasks** | Each group contains several tasks. The information for all tasks of the group will be stored in an array. |
| **Geometry** | The group geometry is defined by the union of all assigned task geometries. |
| **Completed Count** |	Once a group has been completely mapped by a volunteer the completed count of the corresponding group will be raised by one. The completed count of the group is used to assess the overall progress of each project. For doing so the completed count is compared to the redundancy required (see Table 2). During the mapping process groups will be served in ascending completed count order. Thus, groups with low completed count will be served first. |

### Results

Results contain information on the user classifications. However, only “Yes”, “Maybe” and “Bad Imagery” classifications are stored as results. Whenever users indicate “No building” by just swiping to the next set of tasks, no data entry is created. “No Building” classifications can only be modelled retrospectively for groups where a user also submitted at least one “Yes”, “Maybe” or “Bad Imagery” classification.

| Parameter | Description |
| --- | --- |
| **Id** | Each result can be identified by its Id. The Id is a combination of task Id and user Id. |
| **Task Id** | Each result corresponds to a specific task, which can be described by its Id. |
| **User Id** | Each result is contributed by a specific user. Users can be identified by their Id. |
| **Timestamp** | The timestamp (in milliseconds since 01-01-1970) provides information on the time the user completed the group and uploaded the result data. Results within the same group are assigned the same timestamp. |
| **Result** | This parameter describes the given answer. 1 corresponds to “Yes”, 2 corresponds to “Maybe” and 3 corresponds to “Bad Imagery”. Each user can only submit one result per task. |
