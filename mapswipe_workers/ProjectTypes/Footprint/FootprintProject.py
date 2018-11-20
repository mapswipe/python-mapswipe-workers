import os
import logging
import ogr
import urllib.request

from mapswipe_workers.basic import auth
from mapswipe_workers.basic.BaseProject import BaseProject
from mapswipe_workers.ProjectTypes.Footprint.FootprintGroup import FootprintGroup
from mapswipe_workers.ProjectTypes.Footprint import GroupingFunctions as g


########################################################################################################################
# A Footprint Project
class FootprintProject(BaseProject):
    """
    The subclass for a project of the type Footprint
    """

    project_type = 2

    ####################################################################################################################
    # INIT - Existing projects from id, new projects from import_key and import_dict                                   #
    ####################################################################################################################
    def __init__(self, project_id, firebase, mysqlDB, import_key=None, import_dict=None):
        """
        The function to init a project

        Parameters
        ----------
        project_id : int
            The id of the project
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        mysqlDB : database connection class
            The database connection to mysql database
        import_key : str, optional
            The key of this import from firebase imports tabel
        import_dict : dict, optional
            The project information to be imported as a dictionary
        """

        super().__init__(project_id, firebase, mysqlDB, import_key, import_dict)

        if not hasattr(self, 'contributors'):
            # we check if the super().__init__ was able to set the contributors attribute (was successful)
            return None

        elif hasattr(self, 'is_new'):
            # this is a new project, which have not been imported

            self.info = {}
            self.info['tileserver'] = import_dict['tileServer']

            try:
                self.info["tileserver_url"] = import_dict['tileserverUrl']
            except:
                self.info["tileserver_url"] = auth.get_tileserver_url(self.info['tileserver'])

            try:
                self.info["layer_name"] = import_dict['wmtsLayerName']
            except:
                self.info["layer_name"] = None

            try:
                self.info['api_key'] = import_dict['apiKey']
            except:
                try:
                    self.info['api_key'] = auth.get_api_key(self.info['tileserver'])
                except:
                    self.info['api_key'] = None

            # ToDO get groups size from import dict
            self.info["group_size"] = 50

            # we need to download the footprint geometries and store locally
            # make sure that we get a direct download link, make sure data is in geojson format

            url = import_dict['inputGeometries']
            file_name = 'data/input_geometries_{}.geojson'.format(self.id)
            urllib.request.urlretrieve(url, file_name)

            # we need to check if the footprint geometries are valid and remove invalid geometries
            valid_geometries_file = self.check_input_geometries(input_geometries_file=file_name)

            # if the check fails we need to delete the local file and stop the init

            # we need to set the "input geometries file" attribute
            self.info["input_geometries_file"] = valid_geometries_file


            del self.is_new
            logging.warning('%s - __init__ - init complete' % self.id)

    def check_input_geometries(self, input_geometries_file):
        """
        The function to validate to input geometry

        Returns
        -------
        err : str or True
            A text based description why the check failed, or True if all tests passed
        """

        driver = ogr.GetDriverByName('GeoJSON')
        datasource = driver.Open(input_geometries_file, 0)
        layer = datasource.GetLayer()

        # Create the output Layer
        outfile = "data/valid_geometries_{}.geojson".format(self.id)
        outDriver = ogr.GetDriverByName("GeoJSON")

        # Remove output shapefile if it already exists
        if os.path.exists(outfile):
            outDriver.DeleteDataSource(outfile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outfile)
        outLayer = outDataSource.CreateLayer("geometries", geom_type=ogr.wkbMultiPolygon)

        # Add input Layer Fields to the output Layer
        inLayerDefn = layer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)

        # Get the output Layer's Feature Definition
        outLayerDefn = outLayer.GetLayerDefn()

        # check if layer is empty
        if layer.GetFeatureCount() < 1:
            err = 'empty file. No geometries provided'
            logging.warning("%s - check_input_geometry - %s" % (self.id, err))
            return False

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                layer.DeleteFeature(feature.GetFID())
                logging.warning("%s - check_input_geometries - deleted invalid feature %s" % (self.id, feature.GetFID()))
                # removed geometry from layer

            # we accept only POLYGON or MULTIPOLYGON geometries
            elif geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
                layer.DeleteFeature(feature.GetFID())
                logging.warning("%s - check_input_geometries - deleted non polygon feature %s" % (self.id, feature.GetFID()))
                # removed geometry from layer

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
            return False

        del datasource
        del outDataSource
        del layer

        logging.warning('%s - check_input_geometry - filtered correct input geometries' % self.id)
        return outfile


    ####################################################################################################################
    # IMPORT - We define a bunch of functions related to importing new projects                                        #
    ####################################################################################################################
    def create_groups(self):
        """
        The function to create groups of footprint geometries

        Returns
        -------
        groups : dict
            The group information containing task information
        """

        raw_groups = g.group_input_geometries(self.info["input_geometries_file"], self.info["group_size"])

        groups = {}
        for group_id, item in raw_groups.items():
            group = FootprintGroup(self, group_id, item['feature_ids'], item['feature_geometries'])
            groups[group.id] = group.to_dict()

        logging.warning("%s - create_groups - created groups dictionary" % self.id)
        return groups

    ####################################################################################################################
    # EXPORT - We define a bunch of functions related to exporting exiting projects                                    #
    ####################################################################################################################
    def aggregate_results(self, mysqlDB):

        m_con = mysqlDB()

        # your sql command

        data = [self.id]
        project_results = m_con.retr_query(sql_query, data)
        # delete/close db connection
        del m_con

        results_list = []
        for row in project_results:
            row_dict = {}

            # your code to create a dictionary

            results_list.append(row_dict)

        logging.warning('got results information from mysql for project: %s. rows = %s' % (self.id, len(project_results)))
        return results_list

