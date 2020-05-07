import os
from osgeo import ogr
from osgeo import osr
import json

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import logger
from mapswipe_workers.base.base_project import BaseProject
from mapswipe_workers.project_types.build_area.build_area_group import BuildAreaGroup
from mapswipe_workers.utils import tile_grouping_functions as grouping_functions
from mapswipe_workers.definitions import CustomError


class BuildAreaProject(BaseProject):
    """
    The subclass for an import of the type Footprint
    """

    def __init__(self, project_draft):
        # this will create the basis attributes
        super().__init__(project_draft)

        # set group size
        self.project_type = project_draft["projectType"]
        self.groupSize = project_draft["groupSize"]
        self.geometry = project_draft["geometry"]
        self.zoomLevel = int(project_draft.get("zoomLevel", 18))
        self.tileServer = self.get_tile_server(project_draft["tileServer"])
        if self.project_type == 4:
            self.tileServerB = self.get_tile_server(project_draft["tileServerB"])

    def validate_geometries(self):
        raw_input_file = (
            f"{DATA_PATH}/input_geometries/" f"raw_input_{self.projectId}.geojson"
        )
        # check if a 'data' folder exists and create one if not
        if not os.path.isdir("{}/input_geometries".format(DATA_PATH)):
            os.mkdir("{}/input_geometries".format(DATA_PATH))

        # write string to geom file
        with open(raw_input_file, "w") as geom_file:
            json.dump(self.geometry, geom_file)

        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(raw_input_file, 0)

        try:
            layer = datasource.GetLayer()
        except AttributeError:
            logger.warning(
                f"{self.projectId}"
                f" - validate geometry - "
                f"Could not get layer for datasource"
            )
            raise CustomError(f"could not get layer for datasource")

        # check if layer is empty
        if layer.GetFeatureCount() < 1:
            logger.warning(
                f"{self.projectId}"
                f" - validate geometry - "
                f"Empty file. "
                f"No geometry is provided."
            )
            raise CustomError(f"Empty file. ")

        # check if more than 1 geometry is provided
        elif layer.GetFeatureCount() > 1:
            logger.warning(
                f"{self.projectId}"
                f" - validate geometry - "
                f"Input file contains more than one geometry. "
                f"Make sure to provide exact one input geometry."
            )
            raise CustomError(f"Input file contains more than one geometry. ")

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                logger.warning(
                    f"{self.projectId}"
                    f" - validate geometry - "
                    f"Geometry is not valid: {geom_name}. "
                    f"Tested with IsValid() ogr method. "
                    f"Probably self-intersections."
                )
                raise CustomError(f"Geometry is not valid: {geom_name}. ")

            # we accept only POLYGON or MULTIPOLYGON geometries
            if geom_name != "POLYGON" and geom_name != "MULTIPOLYGON":
                logger.warning(
                    f"{self.projectId}"
                    f" - validate geometry - "
                    f"Invalid geometry type: {geom_name}. "
                    f'Please provide "POLYGON" or "MULTIPOLYGON"'
                )
                raise CustomError(f"Invalid geometry type: {geom_name}. ")

            # get geometry as wkt
            wkt_geometry = feat_geom.ExportToWkt()

            # check size of project make sure its smaller than  5,000 sqkm
            # for doing this we transform the geometry into Mollweide projection (EPSG Code 54009)
            source = feat_geom.GetSpatialReference()
            target = osr.SpatialReference()
            target.ImportFromProj4(
                "+proj=moll +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
            )

            transform = osr.CoordinateTransformation(source, target)
            feat_geom.Transform(transform)
            project_area = feat_geom.GetArea() / 1000000

            # calculate max area based on zoom level
            # for zoom level 18 this will be 5000 square kilometers
            # max zoom level is 22
            if self.zoomLevel > 22:
                raise CustomError(
                    f"zoom level is to large (max: 22): {self.zoomLevel}."
                )

            max_area = (23 - int(self.zoomLevel)) * (23 - int(self.zoomLevel)) * 200

            if project_area > max_area:
                logger.warning(
                    f"{self.projectId}"
                    f" - validate geometry - "
                    f"Project is to large: {project_area} sqkm. "
                    f"Please split your projects into smaller sub-projects and resubmit"
                )
                raise CustomError(
                    f"Project is to large: {project_area} sqkm. Max area for zoom level {self.zoomLevel} = {max_area} sqkm"
                )

        del datasource
        del layer

        self.validInputGeometries = raw_input_file

        logger.info(
            f"{self.projectId}" f" - validate geometry - " f"input geometry is correct."
        )

        return wkt_geometry

    def create_groups(self):
        """
        The function to create groups from the project extent
        """
        # first step get properties of each group from extent
        raw_groups = grouping_functions.extent_to_slices(
            self.validInputGeometries, self.zoomLevel, self.groupSize
        )

        for group_id, slice in raw_groups.items():
            group = BuildAreaGroup(self, group_id, slice)
            group.create_tasks(self)
            self.groups.append(group)

        logger.info(
            f"{self.projectId}" f" - create_groups - " f"created groups dictionary"
        )
