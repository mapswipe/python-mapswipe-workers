import os
import logging
import urllib.request
import ogr

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import CustomError
from mapswipe_workers import auth
from mapswipe_workers.base.base_project_draft import BaseProjectDraft
from mapswipe_workers.project_types.footprint import grouping_functions as g
from mapswipe_workers.project_types.footprint.footprint_group import FootprintGroup

########################################################################################################################
# A Footprint Import


class FootprintProjectDraft(BaseProjectDraft):
    """
    The subclass for an import of the type Footprint
    """

    projectType = 2

    def __init__(self, project_draft):
        # this will create the basis attributes
        super().__init__(project_draft)

        # set group size
        self.groupSize = 50
        self.inputGeometries = project_draft['inputGeometries']

        self.validate_geometries()

    def validate_geometries(self):
        raw_input_file = '{}/input_geometries/raw_input_{}.geojson'.format(DATA_PATH, self.projectId)
        valid_input_file = '{}/input_geometries/valid_input_{}.geojson'.format(DATA_PATH, self.projectId)

        if not os.path.isdir('{}/input_geometries'.format(DATA_PATH)):
            os.mkdir('{}/input_geometries'.format(DATA_PATH))

        # download file from given url
        url = self.inputGeometries
        urllib.request.urlretrieve(url, raw_input_file)
        logging.warning(
                f'{self.projectId}' 
                f' - __init__ - downloaded input geometries from url and saved as file: ' 
                f'{raw_input_file}'
                )
        self.inputGeometries = raw_input_file

        # open the raw input file and get layer
        driver = ogr.GetDriverByName('GeoJSON')
        datasource = driver.Open(raw_input_file, 0)
        try:
            layer = datasource.GetLayer()
            LayerDefn = layer.GetLayerDefn()
        except AttributeError:
            raise CustomError('Value error in input geometries file')

        # create layer for valid_input_file to store all valid geometries
        outDriver = ogr.GetDriverByName("GeoJSON")
        # Remove output geojson if it already exists
        if os.path.exists(valid_input_file):
            outDriver.DeleteDataSource(valid_input_file)
        outDataSource = outDriver.CreateDataSource(valid_input_file)
        outLayer = outDataSource.CreateLayer("geometries", geom_type=ogr.wkbMultiPolygon)
        for i in range(0, LayerDefn.GetFieldCount()):
            fieldDefn = LayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)
        outLayerDefn = outLayer.GetLayerDefn()

        # check if raw_input_file layer is empty
        if layer.GetFeatureCount() < 1:
            err = 'empty file. No geometries provided'
            logging.warning(
                    f'{self.projectId} - check_input_geometry - {err}'
                    )
            raise Exception(err)

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                layer.DeleteFeature(feature.GetFID()) # removed geometry from layer
                logging.warning(
                    f'{self.projectId}'
                    f' - check_input_geometries - '
                    f'deleted invalid feature {feature.GetFID()}'
                    )

            # we accept only POLYGON or MULTIPOLYGON geometries
            elif geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
                layer.DeleteFeature(feature.GetFID()) # removed geometry from layer
                logging.warning(
                    f'{self.projectId}'
                    f' - check_input_geometries - '
                    f'deleted non polygon feature {feature.GetFID()}'
                    )

            else:
                # Create output Feature
                outFeature = ogr.Feature(outLayerDefn)
                # Add field values from input Layer
                for i in range(0, outLayerDefn.GetFieldCount()):
                    outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), feature.GetField(i))
                outFeature.SetGeometry(feat_geom)
                outLayer.CreateFeature(outFeature)
                outFeature = None

        # check if layer is empty
        if layer.GetFeatureCount() < 1:
            err = 'no geometries left after checking validity and geometry type.'
            logging.warning(f'{self.projectId} - check_input_geometry - {err}')
            raise Exception(err)

        del datasource
        del outDataSource
        del layer

        self.validInputGeometries = valid_input_file

        logging.warning(
                f'{self.projectId}'
                f' - check_input_geometry - '
                f'filtered correct input geometries and created file: {valid_input_file}'
                )
        return True

    def create_groups(self, project):
        """
        The function to create groups of footprint geometries
        """

        raw_groups = g.group_input_geometries(self.validInputGeometries, self.groupSize)

        for group_id, item in raw_groups.items():
            group = FootprintGroup(self, group_id)
            group.create_tasks(item['feature_ids'], item['feature_geometries'])
            self.groups.append(group)

        logging.warning(f'{project.projectId} - create_groups - created groups dictionary')
