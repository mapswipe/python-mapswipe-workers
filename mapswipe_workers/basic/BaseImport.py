import os
import logging
import json
import csv

from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.utils import error_handling
from mapswipe_workers.basic import BaseFunctions as b
from mapswipe_workers.basic import auth


class BaseImport(object):
    """
    The basic class for an import

    Attributes
    ----------
    project_draft_id: str
        The key of a project draft as depicted in firebase
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

    def __init__(self, project_draft_id, project_draft):
        """
        The function to initialize a new import

        Parameters
        ----------
        project_draft_id : str
        project_draft: dict
            A dictionary containing all attributes of the project_draft

        Returns
        -------
        bool
           True if successful. False otherwise.
        """

        # check if the submission key is correct
        submission_key = project_draft['submissionKey']
        if not submission_key == auth.get_submission_key():
            raise Exception(f"submission key is not valid: {submission_key}")

        logging.warning(f'{submission_key} - __init__ - start init')

        self.project_draft_id = project_draft_id
        self.project_type = project_draft['projectType'],
        self.name = project_draft['name']
        self.image = project_draft['image']
        self.look_for = project_draft['lookFor']
        self.project_details = project_draft['projectDetails']
        self.verification_count = int(project_draft['verificationCount'])

        # eveything else will be stored in the info dict
        self.info = {}
        for key in project_draft.keys():
            if key not in [
                    'name',
                    'image',
                    'lookFor',
                    'projectDetails',
                    'verificationCount',
                    'projectType'
                    'submissionKey'
                    ]:
                self.info[key] = project_draft[key]


    def create_project(self):
        """
        The function to import a new project in firebase and postgres.

        Returns
        -------
        tuple
            project_id and project_type
        """

        fb_db = auth.firebaseDB()
        psql_db = auth.psqlDB()

        projects_ref = fb_db.reference('projects/')
        groups_ref = fb_db.reference('groups/')
        tasks_ref = fb_db.reference('tasks/')

        try:
            logging.warning(f'{self.project_draft_id}\
                    - import_project - start importing')

            # create a new empty project in firebase
            new_project_ref = projects_ref.push()
            # get the project id of new created project
            project_id = new_project_ref.key

            # create groups and tasks for this project.
            # this function is defined by the respective type of this project
            groups = self.create_groups(project_id)

            # extract tasks from groups
            tasks = {}
            for group in groups:
                tasks[group.id] = group['tasks']
                del group['tasks']

            project = {
                "id": project_id,
                "projectType": self.project_type,
                "name": self.name,
                "image": self.image,
                "lookFor": self.look_for,
                "projectDetails": self.project_details,
                "verificationCount": self.verification_count,
                "projectDraftId": self.project_draft_id,
                "info": self.info,
                "isFeatured": False,
                "status": 'inactive',
                "groupAverage": 0,
                "progress": 0,
                "contributors": 0
            }

            # upload data to postgres
            self.execute_import_queries(
                    pg_db,
                    project_id,
                    project,
                    groups,
                    tasks,
                    )

            # upload data to firebase
            new_project_ref.set(project)
            logging.warning('%s - uploaded project in firebase' % project['id'])

            new_groups_ref = (f'{groups_ref}/{project_id}/')
            new_groups.ref.set(groups)
            logging.warning('%s - uploaded groups in firebase' % project_id)

            new_tasks_ref = (f'{tasks_ref}/{project_id}/')
            new_tasks_ref.set(tasks)
            logging.warning('%s - uploaded tasks in firebase' % project_id)

            # TODO
            # # set import complete in firebase
            # self.set_import_complete(firebase)
            # logging.warning('%s - import_project - import finished' % self.import_key)
            # logging.warning('%s - import_project - imported new project with id: %s' % (self.import_key, project_id))
            # upload data to firebase

            return project_id

        except Exception as e:
            logging.warning('%s - import_project - could not import project' % self.project_draft_id)
            logging.warning("%s - import_project - %s" % (self.project_draft_id, e))
            error_handling.log_error(e, logging)

            return (None, None)


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
        # TODO: Delete this function when made sure it is not used anymore

        fb_db = firebase.database()
        fb_db.requests.get = b.myRequestsSession().get

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


    def execute_import_queries(self, project_id, project, groups):
        '''
        Defines SQL queries and data for import a project into postgres.
        SQL queries will be executed as transaction.
        (Either every query will be executed or none)
        '''
        # TODO: Where will this function be called? -> In create_project()

        query_insert_import = '''
            INSERT INTO projectDrafts
            VALUES (%s,%s);
            '''

        data_import = [self.project_draft_id, json.dumps(vars(self))]

        query_insert_project = '''
            INSERT INTO projects
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            '''


        data_project = [
            int(project_dict['contributors']),
            int(project_dict['groupAverage']),
            int(project_dict['id']),
            project_dict['image'],
            project_dict['projectDraftId'],
            project_dict['isFeatured'],
            project_dict['lookFor'],
            project_dict['name'],
            project_dict['progress'],
            project_dict['projectDetails'],
            project_dict['status'],
            int(project_dict['verificationCount']),
            int(project_dict['projectType']),
            json.dumps(project_dict['info'])
        ]

        query_recreate_raw_groups = '''
            DROP TABLE IF EXISTS raw_groups CASCADE;
            CREATE TABLE raw_groups (
              project_id int,
              group_id int,
              count int,
              completedCount int,
              verificationCount int,
              info json,
              PRIMARY KEY (group_id, project_id),
              FOREIGN KEY (project_id) REFERENCES projects(project_id)
            );
            '''

        query_insert_raw_groups = '''
            INSERT INTO groups
            SELECT *
            FROM raw_groups;
            DROP TABLE IF EXISTS raw_groups CASCADE;
            '''

        query_recreate_raw_tasks = '''
            DROP TABLE IF EXISTS raw_tasks CASCADE;
            CREATE TABLE raw_tasks (
                task_id varchar,
                group_id int,
                project_id int,
                info json,
                PRIMARY KEY (task_id, group_id, project_id),
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (group_id) REFERENCES groups(group_id)
            );
            '''

        query_insert_raw_tasks = '''
            INSERT INTO tasks
            SELECT *
            FROM raw_tasks;
            DROP TABLE IF EXISTS raw_tasks CASCADE;
            '''

        groups_txt_filename = self.create_groups_txt_file(project_id, groups)
        tasks_txt_filename = self.create_tasks_txt_file(project_id, groups)

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
                'count',
                'completedCount',
                'verificationCount',
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
                    if key not in [
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


    def create_tasks_txt_file(self, project_id, tasks):
        """
        Creates a text file containing tasks information for a specific project.
        It interates over groups and extracts tasks.
        The text file is temporary and used only by BaseImport module.

        Parameters
        ----------
        project_id : int
            The id of the project
        tasks : dictionary
            Dictionary containing tasks of a project

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

        for group in tasks:
            group_id = int(group)
            for task in group:
                try:
                    output_dict = {
                            "task_id": str(task),
                            "project_id": task['project_id'],
                            "group_id": group_id,
                            "info": {}
                            }
                    for key in task.keys():
                        if key not in ['task_id', 'projectId', 'group_id']:
                            output_dict['info'][key] = [task][key]
                    output_dict['info'] = json.dumps(output_dict['info'])

                    w.writerow(output_dict)
                except Exception as e:
                    logging.warning('%s - set_tasks_postgres - tasks missed critical information: %s' % (project_id, e))

        tasks_txt_file.close()
        return tasks_txt_filename


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
        # TODO: Do we need this funciton?

        fb_db = firebase.database()
        fb_db.child("imports").child(self.project_draft_id).child('complete').set(True)

        logging.warning(f'{self.project_draft_id}\
                - set_import_complete - set import complete')
        return True
