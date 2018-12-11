## Use Cases

### How to identify "good" mapping tasks for MapSwipe

MapSwipe projects can cover large areas in comparison to other mapping approaches, e.g. using the HOT Tasking Manager. Nevertheless, the level of detail of the resulting information you can expect from the resulting data will be lower than using the data from OpenStreetMap.

Here is a list of characteristics that apply to many projects we have in MapSwipe and that may also indicate how suitable your project is for MapSwipe:

* the features you want to map are relatively easy to spot and distinguish from other objects on satellite image with a resolution of around 0.3-0.5 meter.
* you are interest only in a limited number of object types, the ideal case would be 1 object type per project
* the area is large, larger than projects you usually see in the HOT Tasking Manager
* the features you want to map cover only some parts of the whole area (e.g. the built-up area is often less than 10% of the whole project area)


### Building Mapping

This has been the focus for most MapSwipe projects. Buildings are relatively easy to spot, since their shape is familiar to most MapSwipe users. However, not all buildings look the same. Some have a rectangular shape, but others are round or build of clay, which makes it difficult to distinguish buildings and the ground. Sometimes also trees may look like a building.

Building mapping can be done at zoom level 18 or higher.

<img src="/img/building_example1.JPG" alt="building_example1" width="250px"><img src="/img/building_example2.JPG" alt="building_example2" width="250px"><img src="/img/building_example3.JPG" alt="building_example3" width="250px">


### Landcover Mapping - e.g. Mangroves

MapSwipe can be used to map other land cover classes or features besides buildings. We are currently exploring, how the MapSwipe approach could be used to map mangrove forests in southeas asia. The difficult aspect of this tasks is to differentiated mangrove forest and other vegetation types, such as grassland or land used for agriculture.

Landcover mapping can be done at various zoom levels depending of the size of the features of interest. For forest mapping you may choose a lower zoom level, whereas more fine grained features also require a higher zoom level.


### OpenStreetMap Data Validation

In the initial phase data from MapSwipe can support the detailed mapping in OpenStreetMap. However, we can also turn MapSwipe into an OSM data validation tool. By combining satellite imagery and OSM data into one image we can check the completeness and quality of existing data in OSM.

This approach can be used to quickly assess area, where new satellite imagery became available and an updating of the already existing OSM data is needed.

Custom tiles for these type of MapSwipe project can be generated using [MapBox Studio](https://www.mapbox.com/mapbox-studio/). There you can style the OSM data overlay and choose several base layers.

<img src="/img/osm_validation_example.png" alt="osm_validation_example" width="250px">
