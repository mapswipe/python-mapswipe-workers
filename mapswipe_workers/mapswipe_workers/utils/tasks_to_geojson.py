from osgeo import ogr
import os
from mapswipe_workers.utils import tile_grouping_functions as t
from mapswipe_workers.project_types.build_area.build_area_group import BuildAreaGroup
from mapswipe_workers.project_types.build_area.build_area_task import BuildAreaTask
from mapswipe_workers.project_types.build_area.build_area_project import (
    BuildAreaProject,
)


from mapswipe_workers.definitions import logger

url = (
    "https://ecn.t0.tiles.virtualearth.net/tiles/a"
    "{quad_key}.jpeg?g=7505&mkt=en-US&token={key}"
)

apiKeyRequired = "AopsdXjtTu-IwNoCTiZBtgRJ1g7yPkzAi65nXplc-eLJwZHYlAIf2yuSY_Kjg3Wn"
apiKey = "AopsdXjtTu-IwNoCTiZBtgRJ1g7yPkzAi65nXplc-eLJwZHYlAIf2yuSY_Kjg3Wn"

tile_server_dict = {
    "name": "bing",
    "url": url,
    "apiKeyRequired": apiKeyRequired,
    "apiKey": apiKey,
    "wmtsLayerName": None,
    "captions": None,
    "date": None,
    "credits": "credits",
}

BuildAreaProject.projectId = 12
BuildAreaProject.zoomLevel = int(18)
BuildAreaProject.tileServer = tile_server_dict

project_area = "/home/tahira/Public/LOKI/Attica/attica_maybe2.geojson"

raw_groups = t.extent_to_slices(project_area, 18, 120)


project = BuildAreaProject

tasks = list()

for group_id, slice in raw_groups.items():
    xMax = slice["xMax"]
    xMin = slice["xMin"]
    yMax = slice["yMax"]
    yMin = slice["yMin"]
    group = BuildAreaGroup(project, group_id, slice)
    # following lines from create_task function
    for TileX in range(int(xMin), int(xMax) + 1):
        for TileY in range(int(yMin), int(yMax) + 1):
            task = BuildAreaTask(group, project, TileX, TileY)
            tasks.append(vars(task))


def tasks_to_geoJson(tasks, outfile):
    """
        The function to create a geojson file from the tasks.

        Parameters
        ----------
        tasks : list of dict's
            a dictionary contains "yMin", "yMax", "xMax", "xMin", "groupId", "taskId"
            and a "geometry" as ogr.Geometry(ogr.wkbPolygon)
        outfile : str
            the path a .geojson file for storing the output

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
    # Create the output Driver
    driver = ogr.GetDriverByName("GeoJSON")
    # Create the output GeoJSON

    if os.path.exists(outfile):
        driver.DeleteDataSource(outfile)

    outDataSource = driver.CreateDataSource(outfile)

    outLayer = outDataSource.CreateLayer(outfile, geom_type=ogr.wkbPolygon)

    outLayer.CreateField(ogr.FieldDefn("groupId", ogr.OFTString))
    outLayer.CreateField(ogr.FieldDefn("taskId", ogr.OFTString))

    for task in tasks:
        geometry = task["geometry"]
        group_id = task["groupId"]
        task_id = task["taskId"]
        geom = ogr.CreateGeometryFromWkt(geometry)

        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(geom)
        outFeature.SetField("groupId", group_id)
        outFeature.SetField("taskId", task_id)
        outLayer.CreateFeature(outFeature)
        outFeature = None

    outDataSource = None
    logger.info("created all %s." % outfile)

    return True


a = tasks_to_geoJson(tasks, "attica_tasks_maybe2.geojson")
