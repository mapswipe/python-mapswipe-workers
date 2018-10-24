import os
import logging
import ogr

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

    def __init__(self, project_id):
        """
        The function to init a project

        Parameters
        ----------
        project_id : int
            The id of the project
        """

        # super() executes fine now
        super().__init__(project_id)

    def set_project_info(self, import_key, import_dict):
        """
        The function to add specific attributes for BuildArea projects

        Parameters
        ----------
        import_key : str
            The key of the import in the firebase imports table
        import_dict : dict
            The dictionary containing all project information including Build Area project specific information
            For Build Area projects the following information is needed:

            kml : str
                The path to the file with the polygon extent geometry of the project
            tileserver : str
                The tileserver to be used for the background satellite imagery
            custom_tileserver_url : str
                The URL of a tileserver with {x}, {y}, {z} place holders
            zoomlevel : int
                The zoomlevel to be used to create mapping tasks

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        super().set_project_info(import_key, import_dict)
        self.info = {}

        try:
            self.info['tileserver'] = import_dict['tileServer']
        except:
            self.info['tileserver'] = 'Bing'

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

        return True

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

    def valid_import(self, firebase, mysqlDB):
        """
        The function to validate the import information
        """

        if not super().valid_import(firebase, mysqlDB):
            return False
        elif not self.check_input_geometry():
            return False
        else:
            logging.warning('import is valid, %s' % self.import_key)
            return True

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
            logging.warning(err)
            return False
            # check if more than 1 geometry is provided
        elif layer.GetFeatureCount() > 1:
            err = 'Input file contains more than one geometry. Make sure to provide exact one input geometry.'
            logging.warning(err)
            return False

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                err = 'geometry is not valid: %s. Tested with IsValid() ogr method. probably self-intersections.' % geom_name
                return False
            # we accept only POLYGON or MULTIPOLYGON geometries
            if geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
                err = 'invalid geometry type: %s. please provide "POLYGON" or "MULTIPOLYGON"' % geom_name
                print(err)
                return False

        del datasource
        del layer

        logging.warning('input geometry is correct.')
        return True


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

        self.groups = groups
        return groups


