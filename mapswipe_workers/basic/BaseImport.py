import os
import logging
import json
import csv

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.utils import error_handling
from mapswipe_workers.basic import BaseFunctions as b


class BaseImport(object):
    """
    The basic class for an import

    Attributes
    ----------
    import_key : str
        The key of an import as depicted in firebase
    name : str
        The name of a project
    project_details : str
        The detailed description of the project
    look_for : str
        The objects of interest / objects to look for in this project
    image: str
        The URL of the header image of the project
    verification_count : int
        The number of users required for each task to be finished
    info : dict
        A dictionary containing further attributes\
                set by specific types of projects
    """

    def __init__(self, import_key, import_dict):
        """
        The function to initialize a new import

        Parameters
        ----------
        import_key : str
            The key of an import as depicted in firebase
        import_dict: dict
            A dictionary containing all attributes of the import

        Returns
        -------
        bool
           True if successful. False otherwise.
        """

        logging.warning('%s - __init__ - start init' % import_key)
        self.import_key = import_key

        # set the attributes from the parameters provided in the import_dict
        self.name = import_dict['project']['name']
        self.image = import_dict['project']['image']
        self.look_for = import_dict['project']['lookFor']
        self.project_details = import_dict['project']['projectDetails']
        self.verification_count = int(import_dict['project']['verificationCount'])

        # eveything else will be stored in the info dict
        self.info = {}

        for key in import_dict.keys():
            if key not in [
                    'name',
                    'image',
                    'lookFor',
                    'projectDetails',
                    'verification_count',
                    'projectType'
                    ]:
                self.info[key] = import_dict[key]


    def create_project(self, firebase, postgres):
        """
        The function to import a new project in firebase and postgres.

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        postgres : database connection class
            The database connection to postgres database

        Returns
        -------
        bool
            True if successful. False otherwise.
        """

        try:
            logging.warning('%s - import_project - start importing' % self.import_key)

            # get a new project id
            project_id = self.get_new_project_id(firebase)

            # create groups dict for this project.
            # this function is defined by the respective type of this project
            groups_dict = self.create_groups(project_id)

            project_dict = {
                "id": project_id,
                "projectType": self.project_type,
                "name": self.name,
                "image": self.image,
                "lookFor": self.look_for,
                "projectDetails": self.project_details,
                "verificationCount": self.verification_count,
                "importKey": self.import_key,
                "info": self.info,
                "isFeatured": False,
                "state": 3,
                "groupAverage": 0,
                "progress": 0,
                "contributors": 0
            }

            # upload data to postgres
            self.execute_import_queries(
                    postgres,
                    project_id,
                    project_dict,
                    groups_dict
                    )

            # upload data to firebase
            self.set_project_firebase(firebase, project_dict)
            self.set_groups_firebase(firebase, project_id, groups_dict)

            # set import complete in firebase
            self.set_import_complete(firebase)
            logging.warning('%s - import_project - import finished' % self.import_key)
            logging.warning('%s - import_project - imported new project with id: %s' % (self.import_key, project_id))
            return True

        except Exception as e:
            logging.warning('%s - import_project - could not import project' % self.import_key)
            logging.warning("%s - import_project - %s" % (self.import_key, e))
            error_handling.log_error(e, logging)
            return False


    def get_new_project_id(self, firebase):
        """
        The function to get a project id which is not used in firebase

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication

        Returns
        -------
        new_project_id : int
            a new project id which has not been used in firebase

        Notes
        -----
            the new project id needs to be increased by more than 1\
                    to avoid firebase json parsed as an array
            more information here:\
                    https://firebase.googleblog.com/2014/04/best-practices-arrays-in-firebase.html
        """

        fb_db = firebase.database()

        project_keys = fb_db.child('projects').shallow().get().val()
        if not project_keys:
            # set mininum project id to 1000, if no project has been imported yet
            project_keys = [1000]

        project_ids = list(map(int, list(project_keys)))
        project_ids.sort()
        highest_project_id = project_ids[-1]

        logging.warning('ALL - get_new_project_id - highest existing project id: %s' % highest_project_id)
        new_project_id = highest_project_id + 2

        logging.warning('ALL - get_new_project_id - returned new project id: %s' % new_project_id)
        return new_project_id


    def execute_import_queries(self, postgres, project_id, project_dict, groups_dict):
        '''
        Defines SQL queries and data for import a project into postgres.
        SQL queries will be executed as transaction.
        (Either every query will be executed or none)
        '''

        query_insert_import = 'INSERT INTO imports Values(%s,%s);'

        data_import = [self.import_key, json.dumps(vars(self))]

        query_insert_project = '''
            INSERT INTO projects Values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            '''

        data_project = [
            int(project_dict['contributors']),
            int(project_dict['groupAverage']),
            int(project_dict['id']),
            project_dict['image'],
            project_dict['importKey'],
            project_dict['isFeatured'],
            project_dict['lookFor'],
            project_dict['name'],
            project_dict['progress'],
            project_dict['projectDetails'],
            int(project_dict['state']),
            int(project_dict['projectType']),
            int(project_dict['verificationCount']),
            json.dumps(project_dict['info'])
        ]

        query_recreate_raw_groups = '''
            DROP TABLE IF EXISTS raw_groups CASCADE;
            CREATE TABLE raw_groups (
              project_id int
              ,group_id int
              ,count int
              ,completedCount int
              ,verificationCount int
              ,info json
                                );
            '''

        query_insert_raw_groups = '''
            INSERT INTO
              groups
            SELECT
              *
            FROM
              raw_groups
            '''

        query_recreate_raw_tasks =  '''
            DROP TABLE IF EXISTS raw_tasks CASCADE;
            CREATE TABLE raw_tasks (
                task_id varchar
                ,group_id int
                ,project_id int
                ,info json
            );
            '''

        query_insert_raw_tasks = '''
            INSERT INTO
              tasks
            SELECT
              *
            FROM
              raw_tasks
            '''

        groups_txt_filename = self.create_groups_txt_file(project_id, groups_dict)
        tasks_txt_filename = self.create_tasks_txt_file(project_id, groups_dict)

        groups_columns = [
                'project_id',
                'group_id',
                'count',
                'completedCount',
                'verificationCount',
                'info'
                ]
        tasks_columns = [
                'task_id',
                'project_id',
                'group_id',
                'info']

        # execution of all SQL-Statements as transaction
        # (either every query gets executed or none)
        try:
            p_con = postgres()
            p_con._db_cur = p_con._db_connection.cursor()
            p_con._db_cur.execute(query_insert_import, data_import)
            p_con._db_cur.execute(query_insert_project, data_project)
            p_con._db_cur.execute(query_recreate_raw_groups, None)
            p_con._db_cur.execute(query_recreate_raw_tasks, None)
            with open(groups_txt_filename, 'r') as groups_file:
                p_con._db_cur.copy_from(
                        groups_file,
                        'raw_groups',
                        sep='\t',
                        null='\\N',
                        size=8192,
                        columns=groups_columns
                        )
            with open(tasks_txt_filename, 'r') as tasks_file:
                p_con._db_cur.copy_from(
                        tasks_file,
                        'raw_tasks',
                        sep='\t',
                        null='\\N',
                        size=8192,
                        columns=tasks_columns
                        )
            p_con._db_cur.execute(query_insert_raw_groups, None)
            p_con._db_cur.execute(query_insert_raw_tasks, None)
            p_con._db_connection.commit()
            p_con._db_cur.close()
        except Exception as e:
            del p_con
            raise

        os.remove(groups_txt_filename)
        os.remove(tasks_txt_filename)


    def create_groups_txt_file(self, project_id, groups):
        """
        Creates a text file containing groups information for a specific project.
        The text file is temporary and used only by BaseImport module.

        Parameters
        ----------
        project_id : int
            The id of the project
        groups : dict
            The dictionary with the group information

        Returns
        -------
        string
            Filename
        """

        if not os.path.isdir('{}/tmp'.format(DATA_PATH)):
            os.mkdir('{}/tmp'.format(DATA_PATH))

        # create txt file with header for later import with copy function into postgres
        groups_txt_filename = '{}/tmp/raw_groups_{}.txt'.format(DATA_PATH, project_id)
        groups_txt_file = open(groups_txt_filename, 'w', newline='')
        fieldnames = (
                'project_id',
                'group_id',
                'completedCount',
                'verificationCount',
                'count',
                'info'
                )
        w = csv.DictWriter(groups_txt_file, fieldnames=fieldnames, delimiter='\t', quotechar="'")

        for group in groups:
            try:
                output_dict = {
                    "project_id": project_id,
                    "group_id": int(groups[group]['id']),
                    "count": int(groups[group]['count']),
                    "completedCount": int(groups[group]['completedCount']),
                    "verificationCount": int(groups[group]['verificationCount']),
                    "info": {}
                }

                for key in groups[group].keys():
                    if not key in [
                            'project_id',
                            'group_id',
                            'count',
                            'completedCount',
                            'verificationCount',
                            'tasks'
                            ]:
                        output_dict['info'][key] = groups[group][key]
                output_dict['info'] = json.dumps(output_dict['info'])

                w.writerow(output_dict)

            except Exception as e:
                logging.warning('%s - set_groups_postgres - groups missed critical information: %s' % (project_id, e))
                error_handling.log_error(e, logging)

        groups_txt_file.close()

        return groups_txt_filename


    def create_tasks_txt_file(self, project_id, groups):
        """
        Creates a text file containing tasks information for a specific project.
        It interates over groups and extracts tasks.
        The text file is temporary and used only by BaseImport module.

        Parameters
        ----------
        project_id : int
            The id of the project
        groups : dictionary
            Dictionary containing groups of a project

        Returns
        -------
        string 
            Filename
        """

        if not os.path.isdir('{}/tmp'.format(DATA_PATH)):
            os.mkdir('{}/tmp'.format(DATA_PATH))

        # save tasks in txt file
        tasks_txt_filename = '{}/tmp/raw_tasks_{}.txt'.format(DATA_PATH, project_id)
        tasks_txt_file = open(tasks_txt_filename, 'w', newline='')

        fieldnames = ('task_id', 'project_id', 'group_id', 'info')
        w = csv.DictWriter(tasks_txt_file, fieldnames=fieldnames, delimiter='\t', quotechar="'")

        for group in groups:
            for task in groups[group]['tasks']:

                try:
                    output_dict = {
                        "task_id": groups[group]['tasks'][task]['id'],
                        "project_id": project_id,
                        "group_id": int(group),
                        "info": {}
                    }

                    for key in groups[group]['tasks'][task].keys():
                        if not key in ['id', 'projectId']:
                            output_dict['info'][key] = groups[group]['tasks'][task][key]
                    output_dict['info'] = json.dumps(output_dict['info'])

                    w.writerow(output_dict)

                except Exception as e:
                    logging.warning('%s - set_tasks_postgres - tasks missed critical information: %s' % (project_id, e))

        tasks_txt_file.close()

        return tasks_txt_filename


    def set_project_firebase(self, firebase, project_dict):
        """
        Upload the project information to the firebase projects table

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        project_dict : dict
            a dictionary containing all project attributes (e.g. Name, Description, Project Type...)

        Returns
        -------
        bool
            True if successful. False otherwise

        Notes
        -----
        We don't upload all information to firebase
        We need to be careful with spelling here
        We do this to avoid uploading groups, etc.
        """

        fb_db = firebase.database()
        fb_db.child("projects").child(project_dict['id']).set(project_dict)
        logging.warning('%s - set_project_firebase - uploaded project in firebase' % project_dict['id'])
        return True


    def set_groups_firebase(self, firebase, project_id, groups):
        """
        The function to upload groups to firebase

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication

        Returns
        -------
        bool
            True if groups have been uploaded to firebase, False otherwise
        """

        # upload groups in firebase
        fb_db = firebase.database()
        fb_db.child("groups").child(project_id).set(groups)
        logging.warning('%s - set_groups_firebase - uploaded groups in firebase' % project_id)


    def set_import_complete(self, firebase):
        """
        The function to set an import as complete by adding a "complete" attribute in firebase

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        project_id : int
            The id of the project
        groups : dictionary
            Dictionary containing groups of a project

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        fb_db = firebase.database()
        fb_db.child("imports").child(self.import_key).child('complete').set(True)

        logging.warning('%s - set_import_complete - set import complete' % self.import_key)
        return True
