import os
import sys

from osgeo import ogr

from mapswipe_workers.definitions import ProjectType, logger
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.tile_map_service_grid.group import Group
from mapswipe_workers.project_types.tile_map_service_grid.project import Project
from mapswipe_workers.project_types.tile_map_service_grid.task import Task
from mapswipe_workers.utils import tile_grouping_functions as t


def tasks_to_geojson(project_extent_file, zoomlevel, outfile):
    """
    The function to create a geojson file from the tasks.

        Parameters
        ----------
        tasks : list of dict's
            a dic. contains: "yMin", "yMax", "xMax", "xMin", "groupId", "taskId"
            and a "geometry" as ogr.Geometry(ogr.wkbPolygon)
        outfile : str
            the path a .geojson file for storing the output

        Returns
        -------
        bool
            True if successful, False otherwise.
    """
    # select a geojson file and pass it as input parameter
    tile_server_dict = {
        "name": "bing",
    }

    project = Project
    project.projectType = ProjectType.BUILD_AREA.value
    project.projectId = "tasks_to_geojson"
    project.zoomLevel = int(zoomlevel)
    project.tileServer = vars(BaseTileServer(tile_server_dict))

    raw_groups = t.extent_to_groups(project_extent_file, project.zoomLevel, 120)

    tasks = list()

    for group_id, slice in raw_groups.items():
        xMax = slice["xMax"]
        xMin = slice["xMin"]
        yMax = slice["yMax"]
        yMin = slice["yMin"]
        group = Group(project, group_id, slice)
        # following lines from create_task function
        for TileX in range(int(xMin), int(xMax) + 1):
            for TileY in range(int(yMin), int(yMax) + 1):
                task = Task(group, project, TileX, TileY)
                tasks.append(vars(task))

    # count tasks
    count_tasks = 0
    for i in tasks:
        count_tasks += 1

    print(count_tasks)
    # Create the output Driver
    driver = ogr.GetDriverByName("GeoJSON")
    # Create the output GeoJSON

    if os.path.exists(outfile):
        driver.DeleteDataSource(outfile)

    outDataSource = driver.CreateDataSource(outfile)

    outLayer = outDataSource.CreateLayer(outfile, geom_type=ogr.wkbPolygon)

    outLayer.CreateField(ogr.FieldDefn("groupId", ogr.OFTString))
    outLayer.CreateField(ogr.FieldDefn("taskId", ogr.OFTString))
    outLayer.CreateField(ogr.FieldDefn("tile_x", ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn("tile_y", ogr.OFTInteger))
    outLayer.CreateField(ogr.FieldDefn("tile_z", ogr.OFTInteger))

    for task in tasks:
        geometry = task["geometry"]
        group_id = task["groupId"]
        task_id = task["taskId"]
        tile_z, tile_x, tile_y = task["taskId"].split("-")
        geom = ogr.CreateGeometryFromWkt(geometry)

        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(geom)
        outFeature.SetField("groupId", group_id)
        outFeature.SetField("taskId", task_id)
        outFeature.SetField("tile_x", int(tile_x))
        outFeature.SetField("tile_y", (tile_y))
        outFeature.SetField("tile_z", (tile_z))
        outLayer.CreateFeature(outFeature)
        outFeature = None

    outDataSource = None
    logger.info("created all %s." % outfile)

    return True


if __name__ == "__main__":
    project_extent_file = sys.argv[1]  # geojson file
    zoomlevel = sys.argv[2]  # zoomlevel as integer
    output_file = project_extent_file.replace(".geojson", "_tasks.geojson")
    print(tasks_to_geojson(project_extent_file, zoomlevel, output_file))
