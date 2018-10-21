import os
import logging

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
    extent : str
        The path to the file with the polygon extent geometry of the project
    tileserver : str
        The tileserver to be used for the background satellite imagery
    custom_tileserver_url : str
        The URL of a tileserver with {x}, {y}, {z} place holders
    api_key : str
        The api key to access tiles from a tileserver
    zoomlevel : int
        The zoomlevel to be used to create mapping tasks
    """

    project_type = 1

    def __init__(self, project_id):
        # super() executes fine now
        super().__init__(project_id)

    def set_project_info(self, import_key, import_dict):
        super().set_project_info(import_key, import_dict)
        self.info = {
            "tileserver": import_dict['tileServer'],
            "zoomlevel": 18
        }

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

    def kml_to_file(self, kml):
        # check if a 'data' folder exists and create one if not
        if not os.path.isdir('data'):
            os.mkdir('data')
        filename = 'data/import_{}.kml'.format(self.id)

        # write string to geom file
        with open(filename, 'w') as geom_file:
            geom_file.write(kml)

        self.info['extent'] = filename

    def check_import(self):
        # we need to check whether all required information are valid
        super().check_import()
        self.check_input_geometry()

    def check_input_geometry(self):
        # we need to check whether the input geometry provided is correct
        logging.warning('checked input geometry')
        pass


    def create_groups(self):

        # first step get properties of each group from extent
        slices = g.extent_to_slices(self.info['extent'], self.info['zoomlevel'])

        groups = {}
        for slice_id, slice in slices.items():
            group = BuildAreaGroup(self, slice_id, slice)
            groups[group.id] = group

        self.groups = groups


