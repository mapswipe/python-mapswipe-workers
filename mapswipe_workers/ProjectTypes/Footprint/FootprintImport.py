import os
import logging
import urllib.request
import ogr

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import CustomError
from mapswipe_workers.basic import auth
from mapswipe_workers.basic.BaseImport import BaseImport
from mapswipe_workers.ProjectTypes.Footprint import GroupingFunctions as g
from mapswipe_workers.ProjectTypes.Footprint.FootprintGroup import FootprintGroup

########################################################################################################################
# A Footprint Import


class FootprintImport(BaseImport):
    """
    The subclass for an import of the type Footprint
    """

    project_type = 2

    def __init__(self, import_key, import_dict):
        # this will create the basis attributes
        super().__init__(import_key, import_dict)

        # set group size
        self.info["groupSize"] = 50

        if not 'inputGeometries' in self.info.keys():
            logging.warning('%s - __init__ - you need to provide a link to a geojson file' % import_key)
            raise Exception('Attribute "inputGeometries" not provided in import_dict.')

        if not 'tileServer' in self.info.keys():
            logging.warning('%s - __init__ - you need to provide a tileserver name' % import_key)
            raise Exception('Attribute "tileServer" not provided in import_dict.')

        # we need to get the tileserver_url
        if not 'tileServerUrl' in self.info.keys():
            try:
                self.info["tileServerUrl"] = auth.get_tileserver_url(self.info['tileServer'])
            except:
                logging.warning('%s - __init__ - we need a tilserver_url for the tileserver: %s' % (import_key, self.info['tileServer']))
                raise Exception('Attribute "tileServerUrl" not provided in import_dict and not in "auth.get_tileserver_url" function.')

        if not 'apiKey' in self.info.keys() and self.info['tileServer'] != 'custom':
            try:
                self.info['apiKey'] = auth.get_api_key(self.info['tileServer'])
            except:
                logging.warning('%s - __init__ - we need an api key for the tileserver: %s' % (import_key, self.info['tileServer']))
                raise Exception('Attribute "api_key" not provided in import_dict and not in "auth.get_api_key" function.')

        self.validate_geometries()


    def validate_geometries(self):

        raw_input_file = '{}/input_geometries/raw_input_{}.geojson'.format(DATA_PATH, self.import_key)
        valid_input_file = '{}/input_geometries/valid_input_{}.geojson'.format(DATA_PATH, self.import_key)

        if not os.path.isdir('{}/import'.format(DATA_PATH)):
            os.mkdir('{}/import'.format(DATA_PATH))

        # download file from given url
        url = self.info['inputGeometries']
        urllib.request.urlretrieve(url, raw_input_file)
        logging.warning('%s - __init__ - downloaded input geometries from url and saved as file: %s' % (self.import_key, raw_input_file))
        self.info['inputGeometries'] = raw_input_file

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
            logging.warning("%s - check_input_geometry - %s" % (self.import_key, err))
            raise Exception(err)

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                layer.DeleteFeature(feature.GetFID()) # removed geometry from layer
                logging.warning("%s - check_input_geometries - deleted invalid feature %s" % (self.import_key, feature.GetFID()))

            # we accept only POLYGON or MULTIPOLYGON geometries
            elif geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
                layer.DeleteFeature(feature.GetFID()) # removed geometry from layer
                logging.warning("%s - check_input_geometries - deleted non polygon feature %s" % (self.import_key, feature.GetFID()))

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
            logging.warning("%s - check_input_geometry - %s" % (self.id, err))
            raise Exception(err)

        del datasource
        del outDataSource
        del layer

        self.info['validInputGeometries'] = valid_input_file

        logging.warning('%s - check_input_geometry - filtered correct input geometries and created file: %s' % (self.import_key, valid_input_file))
        return True

    def create_groups(self, project_id) -> dict:
        """
        The function to create groups of footprint geometries

        Returns
        -------
        groups : dict
            The group information containing task information
        """

        raw_groups = g.group_input_geometries(self.info["validInputGeometries"], self.info["groupSize"])

        groups = {}
        for group_id, item in raw_groups.items():
            group = FootprintGroup(self, project_id, group_id, item['feature_ids'], item['feature_geometries'])
            groups[group.id] = group.to_dict()

        logging.warning("%s - create_groups - created groups dictionary" % project_id)
        return groups
