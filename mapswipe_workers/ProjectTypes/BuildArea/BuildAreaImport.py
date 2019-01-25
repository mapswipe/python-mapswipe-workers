import os
import logging
import ogr

from mapswipe_workers.basic import auth
from mapswipe_workers.basic.BaseImport import BaseImport
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaGroup import BuildAreaGroup
from mapswipe_workers.ProjectTypes.BuildArea import GroupingFunctions as g

########################################################################################################################
# A Footprint Import

class BuildAreaImport(BaseImport):
    """
    The subclass for an import of the type Footprint
    """

    project_type = 1

    def __init__(self, import_key, import_dict, output_path):
        # this will create the basis attributes
        super().__init__(import_key, import_dict, output_path)

        # set group size
        self.info["groupSize"] = 50

        if not 'kml' in self.info.keys():
            logging.warning('%s - __init__ - you need to provide a kml geometry' % import_key)
            raise Exception('Attribute "kml" not provided in import_dict.')

        if not 'tileServer' in self.info.keys():
            logging.warning('%s - __init__ - you need to provide a tileserver name' % import_key)
            raise Exception('Attribute "tileServer" not provided in import_dict.')

        if not 'zoomLevel' in self.info.keys():
            logging.warning('%s - __init__ - you need to provide a zoom level name' % import_key)
            self.info['zoomLevel'] = 18
            logging.warning('%s - __init__ - we set zoom level to 18' % import_key)

        # we need to get the tileserver_url
        if not 'tileServerUrl' in self.info.keys():
            try:
                self.info["tileServerUrl"] = auth.get_tileserver_url(self.info['tileServer'])
            except:
                logging.warning('%s - __init__ - we need a tilserver_url for the tileserver: %s' % (
                import_key, self.info['tileServer']))
                raise Exception(
                    'Attribute "tileServerUrl" not provided in import_dict and not in "auth.get_tileserver_url" function.')

        if not 'apiKey' in self.info.keys() and self.info['tileServer'] != 'custom':
            try:
                self.info['apiKey'] = auth.get_api_key(self.info['tileServer'])
            except:
                logging.warning(
                    '%s - __init__ - we need an api key for the tileserver: %s' % (import_key, self.info['tileServer']))
                raise Exception(
                    'Attribute "api_key" not provided in import_dict and not in "auth.get_api_key" function.')

        if not 'layerName' in self.info.keys():
            self.info['layerName'] = None

        self.validate_geometries(output_path)

    def validate_geometries(self, output_path):

        raw_input_file = '{}/import/raw_input_{}.kml'.format(output_path, self.import_key)

        # check if a 'data' folder exists and create one if not
        if not os.path.isdir('{}/import'.format(output_path)):
            os.mkdir('{}/import'.format(output_path))

        # write string to geom file
        with open(raw_input_file, 'w') as geom_file:
            geom_file.write(self.info['kml'])


        driver = ogr.GetDriverByName('KML')
        datasource = driver.Open(raw_input_file, 0)
        layer = datasource.GetLayer()

        # check if layer is empty
        if layer.GetFeatureCount() < 1:
            err = 'empty file. No geometries provided'
            logging.warning("%s - check_input_geometry - %s" % (self.import_key, err))
            return False
            # check if more than 1 geometry is provided
        elif layer.GetFeatureCount() > 1:
            err = 'Input file contains more than one geometry. Make sure to provide exact one input geometry.'
            logging.warning("%s - check_input_geometry - %s" % (self.import_key, err))
            return False

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            if not feat_geom.IsValid():
                err = 'geometry is not valid: %s. Tested with IsValid() ogr method. probably self-intersections.' % geom_name
                logging.warning("%s - check_input_geometry - %s" % (self.import_key, err))
                return False
            # we accept only POLYGON or MULTIPOLYGON geometries
            if geom_name != 'POLYGON' and geom_name != 'MULTIPOLYGON':
                err = 'invalid geometry type: %s. please provide "POLYGON" or "MULTIPOLYGON"' % geom_name
                logging.warning("%s - check_input_geometry - %s" % (self.import_key, err))
                return False

        del datasource
        del layer

        self.info['validInputGeometries'] = raw_input_file

        logging.warning('%s - check_input_geometry - input geometry is correct.' % self.import_key)
        return True


    def create_groups(self, project_id):
        """
        The function to create groups from the project extent

        Returns
        -------
        groups : dict
            The group information containing task information
        """

        # first step get properties of each group from extent
        raw_groups = g.extent_to_slices(self.info['validInputGeometries'], self.info['zoomLevel'])

        groups = {}
        for group_id, slice in raw_groups.items():
            group = BuildAreaGroup(self, project_id, group_id, slice)
            groups[group.id] = group.to_dict()

        logging.warning("%s - create_groups - created groups dictionary" % self.import_key)
        return groups


