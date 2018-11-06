import os
import logging
import ogr
import json
import pandas as pd

from mapswipe_workers.cfg import auth
from mapswipe_workers.basic.BaseProject import BaseProject
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaGroup import BuildAreaGroup
from mapswipe_workers.ProjectTypes.BuildArea import GroupingFunctions as g

########################################################################################################################
# A Build Area Project
class BuildAreaProject(BaseProject):
    """
    The subclass for a project of the type BuildArea

    Attributes
    ----------
    project_type : int
        The type of the project
        project_type is always 1 for Build Area projects

    info : dict
        A dictionary containing all Build Area project specific information

        extent : str
            The path to the file with the polygon extent geometry of the project
        tileserver : str
            The tileserver to be used for the background satellite imagery
        custom_tileserver_url : str
            The URL of a tileserver with {x}, {y}, {z} place holders
        api_key : str, optional
            The api key to access tiles from a tileserver
        zoomlevel : int
            The zoomlevel to be used to create mapping tasks
    """

    project_type = 1

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

        # we check if the super().__init__ was able to set the contributors attribute (was successful)
        if not hasattr(self, 'contributors'):
            return None
        elif not hasattr(self, 'is_new'):
            # this is a project which has already been imported
            # if no tileserver is specified we will default to Bing
            try:
                self.info['tileserver']
            except:
                self.info['tileserver'] = 'bing'

            # if no zoomlevel is specified we will default to 18
            try:
                self.info['zoomlevel']
            except:
                self.info['zoomlevel'] = 18

            if self.info['tileserver'] != 'custom':
                try:
                    self.info['api_key']
                except:
                    self.info['api_key'] = auth.get_api_key(self.info['tileserver'])
            else:
                self.info['api_key'] = None

            # this is an optional parameter not used by all projects
            try:
                self.info['custom_tileserver_url']
            except:
                self.info['custom_tileserver_url'] = None

            try:
                self.info['extent']
            except:
                self.info['extent'] = None

            logging.warning('%s - __init__ - init complete' % self.id)
        elif hasattr(self, 'is_new'):
            # this is a new project, which have not been imported
            self.info = {}
            try:
                self.info['tileserver'] = import_dict['tileServer']
            except:
                self.info['tileserver'] = 'bing'

            try:
                self.info['zoomlevel'] = import_dict['zoomLevel']
            except:
                self.info['zoomlevel'] = 18

            # get api key for tileserver
            if self.info['tileserver'] != 'custom':
                self.info['api_key'] = auth.get_api_key(self.info['tileserver'])
            else:
                self.info['api_key'] = None

            try:
                self.info['custom_tileserver_url'] = import_dict['custom_tileserver_url']
            except:
                self.info['custom_tileserver_url'] = None

            self.kml_to_file(import_dict['kml'])
            if not self.check_input_geometry():
                logging.warning("%s - __init__ - project geometry is invalid. can't init project" % self.id)
                return None

            del self.is_new
            logging.warning('%s - __init__ - init complete' % self.id)

    def kml_to_file(self, kml, outpath='data'):
        """
        The function to save a kml string as a file

        Parameters
        ----------
        kml : str
            The polygon geometry as kml string
        outpath : str
            The output directory of the kml file to be created

        Returns
        -------
        extent : str
            The path of the created kml file
        """

        # check if a 'data' folder exists and create one if not
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        filename = '{}/import_{}.kml'.format(outpath, self.id)

        # write string to geom file
        with open(filename, 'w') as geom_file:
            geom_file.write(kml)

        self.info['extent'] = filename
        return filename

    def check_input_geometry(self):
        """
        The function to validate to input geometry
            Check will fail if:
            * no geometry provided
            * more than one geometry provided
            * invalid geometry provided
            * non-polygon geometry provided

        Returns
        -------
        err : str or True
            A text based description why the check failed, or True if all tests passed
        """

        driver = ogr.GetDriverByName('KML')
        datasource = driver.Open(self.info['extent'], 0)
        layer = datasource.GetLayer()

        # check if layer is empty
        if layer.GetFeatureCount() < 1:
            err = 'empty file. No geometries provided'
            logging.warning("%s - check_input_geometry - %s" % (self.id, err))
            return False
            # check if more than 1 geometry is provided
        elif layer.GetFeatureCount() > 1:
            err = 'Input file contains more than one geometry. Make sure to provide exact one input geometry.'
            logging.warning("%s - check_input_geometry - %s" % (self.id, err))
            return False

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                err = 'geometry is not valid: %s. Tested with IsValid() ogr method. probably self-intersections.' % geom_name
                logging.warning("%s - check_input_geometry - %s" % (self.id, err))
                return False
            # we accept only POLYGON or MULTIPOLYGON geometries
            if geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
                err = 'invalid geometry type: %s. please provide "POLYGON" or "MULTIPOLYGON"' % geom_name
                logging.warning("%s - check_input_geometry - %s" % (self.id, err))
                return False

        del datasource
        del layer

        logging.warning('%s - check_input_geometry - input geometry is correct.' % self.id)
        return True

    ####################################################################################################################
    # IMPORT - We define a bunch of functions related to importing new projects                                        #
    ####################################################################################################################
    def create_groups(self):
        """
        The function to create groups from the project extent

        Returns
        -------
        groups : dict
            The group information containing task information
        """

        # first step get properties of each group from extent
        slices = g.extent_to_slices(self.info['extent'], self.info['zoomlevel'])

        groups = {}
        for slice_id, slice in slices.items():
            group = BuildAreaGroup(self, slice_id, slice)
            groups[group.id] = group

        logging.warning("%s -- create_groups -- created groups dictionary" % self.id)
        return groups

    ####################################################################################################################
    # EXPORT - We define a bunch of functions related to exporting exiting projects                                    #
    ####################################################################################################################
    def aggregate_results(self, mysqlDB, mysql_results):

        # aggregate by task_id
        agg_dict = {
            'task_id': {
                'task_count': 'count'
            },
            'result': {
                'average_result': 'mean',
                'yes_count': lambda x: x == 1
            }
        }

        # group by task_id and aggregate
        df = mysql_results.groupby('task_id').agg(agg_dict)
        print(df)

        return df







