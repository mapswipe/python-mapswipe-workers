import os
import logging
import json
import csv

from mapswipe_workers.utils import error_handling
from mapswipe_workers.basic import BaseFunctions as b


class BaseImport(object):

    def __init__(self, import_key, import_dict, output_path):

        logging.warning('%s - __init__ - start init' % import_key)
        self.import_key = import_key

        # let's set the attributes from the parameters provided in the import_dict
        self.name = import_dict['project']['name']
        self.image = import_dict['project']['image']
        self.look_for = import_dict['project']['lookFor']
        self.project_details = import_dict['project']['projectDetails']
        self.verification_count = int(import_dict['project']['verificationCount'])

        # eveything else will be stored in the info dict
        self.info = {}

        for key in import_dict.keys():
            if key not in ['name', 'image', 'lookFor', 'projectDetails', 'verification_count', 'projectType']:
                self.info[key] = import_dict[key]

    def create_project(self, firebase, postgres, output_path):
        """
        The function to import a new project

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

            # create groups dict for this project. this function is defined by the respective type of this project
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
            self.set_import_postgres(postgres)
            self.set_project_postgres(postgres, project_dict)
            self.set_groups_postgres(postgres, project_id, groups_dict, output_path)
            self.set_tasks_postgres(postgres, project_id, groups_dict, output_path)

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

            # ToDO need to check how to delete if project could not be imported.
            b.delete_project_postgres(project_id, self.import_key, postgres)
            b.delete_project_firebase(project_id, self.import_key, firebase)
            b.delete_local_files(project_id, self.import_key, output_path)
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
            the new project id needs to be increased by more than 1 to avoid firebase json parsed as an array
            more information here: https://firebase.googleblog.com/2014/04/best-practices-arrays-in-firebase.html
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

    def set_import_postgres(self, postgres):
        """
        The function saves the import information from firebase to the posgres imports table

        Parameters
        ----------
        postgres : database connection class
            The database connection to postgres database
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication

        Returns
        -------
        bool
            True if successful. False otherwise

        """

        p_con = postgres()
        sql_insert = "INSERT INTO imports Values(%s,%s)"

        data = [self.import_key, json.dumps(vars(self))]
        # insert in table
        try:
            p_con.query(sql_insert, data)
        except Exception as e:
            del p_con
            raise

        logging.warning('%s - set_imports_postgres - inserted import info in postgres' % self.import_key)
        return True

    def set_project_postgres(self, postgres, project_dict):
        """
        The function to create a project in postgres
        Parameters
        ----------
        postgres : database connection class
            The database connection to postgres database

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        p_con = postgres()
        sql_insert = "INSERT INTO projects Values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        data = [
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

        # insert in table
        try:
            p_con.query(sql_insert, data)
        except Exception as e:
            del p_con
            raise

        logging.warning('%s - set_project_postgres - inserted project info in postgres' % project_dict['id'])
        return True

    def set_groups_postgres(self, postgres, project_id, groups, output_path):
        """
        The function to import all groups for the project into postgres groups table

        Parameters
        ----------
        postgres : database connection class
            The database connection to postgres database
        groups : dict
            The dictionary with the group information
        groups_txt_filename : str
            The path where a temporary txt file will be stored to import into postgres

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        if not os.path.isdir('{}/tmp'.format(output_path)):
            os.mkdir('{}/tmp'.format(output_path))

        # create txt file with header for later import with copy function into postgres
        groups_txt_filename = '{}/tmp/raw_groups_{}.txt'.format(output_path, project_id)
        groups_txt_file = open(groups_txt_filename, 'w', newline='')
        fieldnames = ('project_id', 'group_id', 'completedCount', 'count', 'info')
        w = csv.DictWriter(groups_txt_file, fieldnames=fieldnames, delimiter='\t', quotechar="'")

        for group in groups:
            try:
                output_dict = {
                    "project_id": project_id,
                    "group_id": int(groups[group]['id']),
                    "count": int(groups[group]['count']),
                    "completedCount": int(groups[group]['completedCount']),
                    "info": {}

                }

                for key in groups[group].keys():
                    if not key in ['project_id', 'group_id', 'count',
                                   'completedCount', 'tasks']:
                        output_dict['info'][key] = groups[group][key]
                output_dict['info'] = json.dumps(output_dict['info'])

                w.writerow(output_dict)

            except Exception as e:
                logging.warning('%s - set_groups_postgres - groups missed critical information: %s' % (project_id, e))
                error_handling.log_error(e, logging)

        groups_txt_file.close()

        p_con = postgres()

        # first create a table for the raw groups information
        sql_insert = '''
            DROP TABLE IF EXISTS raw_groups CASCADE;
            CREATE TABLE raw_groups (
              project_id int
              ,group_id int
              ,count int
              ,completedCount int
              ,info json
                                );
            '''

        p_con.query(sql_insert, None)

        # insert data from txt file into raw groups table in postgres
        f = open(groups_txt_filename, 'r')
        columns = ['project_id', 'group_id', 'count', 'completedCount', 'info']
        p_con.copy_from(f, 'raw_groups', sep='\t', columns=columns)
        logging.warning('%s - set_groups_postgres - inserted raw groups into table raw_groups' % project_id)
        f.close()
        os.remove(groups_txt_filename)
        logging.warning('%s - set_groups_postgres - deleted file: %s' % (project_id, groups_txt_filename))

        # insert groups into postgres groups table and handle conflicts
        sql_insert = '''
                        INSERT INTO
                          groups
                        SELECT
                          *
                          -- duplicates is set to zero by default, this will be updated on conflict only
                          --,0
                        FROM
                          raw_groups
                        --ON CONFLICT ON CONSTRAINT "tasks_pkey";

                    '''
        p_con.query(sql_insert, None)
        del p_con

        logging.warning('%s - set_groups_postgres - inserted groups into groups table' % project_id)
        return True

    def set_tasks_postgres(self, postgres, project_id, groups, output_path):
        """
        The function iterates over the groups and extracts tasks and uploads them into postgresql
        Parameters
        ----------
        postgres : database connection class
            The database connection to postgres database
        groups : dictionary
            Dictionary containing groups of a project
        tasks_txt_filename : string
            Pointer for storing the tasks temporary in csv format

        Returns
        -------
        bool
            True if successful. False otherwise

        """

        if not os.path.isdir('{}/tmp'.format(output_path)):
            os.mkdir('{}/tmp'.format(output_path))

        # save tasks in txt file
        tasks_txt_filename = '{}/tmp/raw_tasks_{}.txt'.format(output_path, project_id)
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

        # upload data to postgres

        p_con = postgres()

        # first importer to a table where we store the geom as text
        sql_insert = '''
            DROP TABLE IF EXISTS raw_tasks CASCADE;
            CREATE TABLE raw_tasks (
                task_id varchar
                ,group_id int
                ,project_id int
                ,info json
            );
            '''

        p_con.query(sql_insert, None)

        f = open(tasks_txt_filename, 'r')
        columns = ['task_id', 'project_id', 'group_id', 'info']
        p_con.copy_from(f, 'raw_tasks', sep='\t', columns=columns)

        logging.warning('%s - set_tasks_postgres - inserted raw tasks into table raw_tasks' % project_id)
        f.close()

        os.remove(tasks_txt_filename)
        logging.warning('%s - set_tasks_postgres - deleted file: %s' % (project_id, tasks_txt_filename))

        # TODO discuss if conflict resolution necessary

        sql_insert = '''
                INSERT INTO
                  tasks
                SELECT
                  *
                  -- duplicates is set to zero by default, this will be updated on conflict only
                  --,0
                FROM
                  raw_tasks
                --ON CONFLICT ON CONSTRAINT "tasks_pkey";

            '''
        p_con.query(sql_insert, None)
        del p_con

        logging.warning('%s - set_tasks_postgres - inserted tasks into tasks table' % project_id)
        return True

    def set_project_firebase(self, firebase, project_dict):
        """
        The function to upload the project information to the firebase projects table

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication

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

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        fb_db = firebase.database()
        fb_db.child("imports").child(self.import_key).child('complete').set(True)

        logging.warning('%s - set_import_complete - set import complete' % self.import_key)
        return True
