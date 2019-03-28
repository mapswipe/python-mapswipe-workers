import os
import logging
import ogr

from mapswipe_workers import auth
from mapswipe_workers.base.base_project import BaseProject
from mapswipe_workers.project_types.build_area.build_area_group import BuildAreaGroup
from mapswipe_workers.project_types.build_area import grouping_functions as g

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
    def __init__(self, project_id, firebase, postgres, import_key=None, import_dict=None):
        """
        The function to init a project

        Parameters
        ----------
        project_id : int
            The id of the project
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        postgres : database connection class
            The database connection to mysql database
        import_key : str, optional
            The key of this import from firebase imports tabel
        import_dict : dict, optional
            The project information to be imported as a dictionary
        """

        super().__init__(project_id, firebase, postgres)
        logging.warning('%s - __init__ - init complete' % self.id)

    ####################################################################################################################
    # EXPORT - We define a bunch of functions related to exporting exiting projects                                    #
    ####################################################################################################################
    def aggregate_results(self, postgres: object) -> dict:
        """
        The Function to aggregate results per task.

        Parameters
        ----------
        postgres : database connection class
            The database connection to postgres database

        Returns
        -------
        results_dict : dict
            result of the aggregation as dictionary. Key for every object is task id. Properties are decision,
            yes_count, maybe_count, bad_imagery_count

        """
        p_con = postgres()
        # sql command
        sql_query = '''
            select
              task_id as id
              ,project_id as project
              ,avg(cast(info ->> 'result' as integer))as decision
              ,SUM(CASE
                WHEN cast(info ->> 'result' as integer) = 1 THEN 1
                ELSE 0
               END) AS yes_count
               ,SUM(CASE
                WHEN cast(info ->> 'result' as integer) = 2 THEN 1
                ELSE 0
               END) AS maybe_count
               ,SUM(CASE
                WHEN cast(info ->> 'result' as integer) = 3 THEN 1
                ELSE 0
               END) AS bad_imagery_count
            from
              results
            where
              project_id = %s and cast(info ->> 'result' as integer) > 0
            group by
              task_id
              ,project_id'''

        header = ['id', 'project_id','decision', 'yes_count', 'maybe_count', 'bad_imagery_count']
        data = [self.id]

        project_results = p_con.retr_query(sql_query, data)
        # delete/close db connection
        del p_con

        results_dict = {}
        for row in project_results:
            row_id = ''
            row_dict = {}
            for i in range(0, len(header)):
                # check for task id
                if header[i] == 'id':
                    row_id = str(row[i])
                elif header[i] == 'decision':  # check for float value
                    row_dict[header[i]] = float(str(row[i]))
                # check for integer value
                elif header[i] in ['yes_count', 'maybe_count', 'bad_imagery_count']:
                    row_dict[header[i]] = int(str(row[i]))
                # all other values will be handled as strings
                else:
                    row_dict[header[i]] = row[i]
            results_dict[row_id] = row_dict

        logging.warning('got results information from postgres for project: %s.'' rows = %s' % (self.id, len(project_results)))
        return results_dict
