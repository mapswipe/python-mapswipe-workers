import os
import logging
import threading
import numpy as np
from queue import Queue
import requests
import time
import json
from psycopg2 import sql
from mapswipe_workers.basic import BaseFunctions as b
from mapswipe_workers.definitions import DATA_PATH

class BaseProject(object):
    """
    The basic class for a project

    Attributes
    ----------
    id : int
        The id of a project
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
    is_featured : bool
        Whether a project is displayed as a featured project in the app
    state : int
        Whether a project is displayed in the app
        0 = displayed
        1 = ???
        2 = ???
        3 = not displayed
    group_average : float
        The average number of tasks per group
    progress : int
        The number of finished tasks in percent
    contributors : int
        The number of users contributing to this project
    """

    ####################################################################################################################
    # INIT - Existing projects from id, new projects from import_key and import_dict                                   #
    ####################################################################################################################
    def __init__(self, project_id: int, firebase: object, postgres: object,) -> object:

        logging.warning('%s - __init__ - start init' % project_id)

        # set basic project information
        self.id = project_id

        # check if project exists in firebase and postgres
        project_exists = b.project_exists(self.id, firebase, postgres)

        if not project_exists:
            raise Exception("can't init project.")
        else:
            fb_db = firebase.database()
            project_data = fb_db.child("projects").child(project_id).get().val()

            # we set attributes based on the data from firebase
            self.import_key = project_data['importKey']
            self.name = project_data['name']
            self.image = project_data['image']
            self.look_for = project_data['lookFor']
            self.project_details = project_data['projectDetails']
            self.verification_count = int(project_data['verificationCount'])
            self.is_featured = project_data['isFeatured']
            self.state = project_data['state']
            self.group_average = project_data['groupAverage']
            self.progress = project_data['progress']
            self.contributors = project_data['contributors']
            # old projects might not have an info field in firebase
            try:
                self.info = project_data['info']
            except:
                self.info = {}

    ####################################################################################################################
    # DELETE - We define a bunch of functions related to delete project information                                    #
    ####################################################################################################################

    def delete_project(self, firebase, postgres):
        """
        The function to delete all project related information in firebase and postgres
            This includes information on groups

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        postgres : database connection class
            The database connection to postgres database

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        logging.warning('%s - delete_project - start deleting project' % self.id)
        b.delete_local_files(self.id, self.import_key)
        b.delete_project_postgres(self.id, self.import_key, postgres)
        b.delete_project_firebase(self.id, self.import_key, firebase)

        logging.warning('%s - delete_project - finished delete project' % self.id)
        return True

    ####################################################################################################################
    # UPDATE - We define a bunch of functions related to updating existing projects                                    #
    ####################################################################################################################
    def update_project(self, firebase, postgres):
        """
        The function to update the progress and contributors of a project in firebase and postgres

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

        self.get_contributors(postgres)
        self.set_contributors(firebase)
        groups_progress_list = self.get_progress(firebase)
        self.set_progress(firebase)
        self.set_project_progress_postgres(postgres)
        self.set_groups_progress_postgres(postgres, groups_progress_list)

    def set_groups_progress_postgres(self, postgres, groups_progress_list):
        """
        The function to set completed count for every group which got new contributions in postgres

        Parameters
        ----------
        groups_progress_list : list

        Returns
        -------
        """

        groups_progress_file_path = DATA_PATH + '/groups_progess.csv'
        groups_progress_file = open(groups_progress_file_path,'w')

        #print(groups_progress_list)
        for item in groups_progress_list:
            if int(item[2]) > 0:
                outline = '%i,%i,%i\n' %(int(item[0]), int(item[1]), int(item[2]))
                groups_progress_file.write(outline)

        groups_progress_file.close()
        groups_progress_file = open(groups_progress_file_path, 'r')

        p_con = postgres()

        # groups_progress_tablename = 'groups_progress'
        groups_progress_columns = ('project_id', 'group_id', 'completedcount')
        sql_insert = '''
                    DROP TABLE IF EXISTS ;
                    CREATE TABLE {} (
                        project_id int
                        ,group_id int
                        ,completedCount int
                    );'''
        sql_insert = sql.SQL(sql_insert).format(sql.Identifier(groups_progress_tablename),
                                                sql.Identifier(groups_progress_tablename))

        p_con.query(sql_insert, None)
        p_con.copy_from(groups_progress_file, groups_progress_tablename, sep=',', columns=groups_progress_columns)
        groups_progress_file.close()

        sql_insert = '''
                UPDATE groups
                SET completedcount = b.completedcount 
                FROM
                    {} as b
                WHERE 
                    groups.group_id = b.group_id
                    and
                    groups.project_id = b.project_id
                    and
                    groups.completedcount =! b.completedcount;
                DROP TABLE IF EXISTS {};
                        '''
        sql_insert = sql.SQL(sql_insert).format(sql.Identifier(groups_progress_tablename),
                                                sql.Identifier(groups_progress_tablename))

        p_con.query(sql_insert, None)

        del p_con
        logging.warning('%s - set_groups_progress_postgres - finished setting groups progress in postgres' % self.id)



    def get_group_progress(self, q):
        """
        The function to get the progress for groups in queue

        Parameters
        ----------
        q : queue
            A queue object containing a list with the following items:
            fb_db : firebase connection
            group_progress_list : list
            group_id : int

        Returns
        -------

        """
        while not q.empty():
            # get the values from the q object
            fb_db, group_progress_list, group_id = q.get()

            # this functions downloads only the completed count per group from firebase
            try:
                # establish a new connection to firebase
                # check for empty group_id, caused by old grouping generation
                if not group_id:
                    continue
                completed_count = fb_db.child("groups").child(self.id).child(group_id).child("completedCount").get().val()

                # progress in percent, progress can't be bigger than 100
                progress = 100.0 * float(completed_count) / float(self.verification_count)
                if progress > 100:
                    progress = 100.0
                # all variables are converted to float to avoid errors when computing the mean later
                group_progress_list.append(
                    [float(self.id), float(group_id), float(completed_count), float(self.verification_count),
                     float(progress)])
                q.task_done()

            except Exception as e:
                # add a catch, if something with the connection to firebase goes wrong and log potential errors
                logging.warning("%s - get_groups_progress - %s" % (self.id,e))
                # if we can't get the completed count for a group, we will set it to 0.0
                completed_count = 0.0
                progress = 0.0
                # all variables are converted to float to avoid errors when computing the mean later
                group_progress_list.append(
                    [float(self.id), float(group_id), float(completed_count), float(self.verification_count),
                     float(progress)])
                q.task_done()

    def get_progress(self, firebase, num_threads=24):
        """
        The function to compute the progress of the project

        Parameters
        ----------
         firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        num_threads : int, optional
            The number of threads to use, default: 24

        Notes
        -----
        We use threading in this function.
        There is no easy way to compute the sum of the completed count for all groups.
        """

        fb_db = firebase.database()
        # this tries to set the max pool connections to 100
        adapter = requests.adapters.HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
        for scheme in ('http://', 'https://'):
            fb_db.requests.mount(scheme, adapter)

        # it is important to use the shallow option, only keys will be loaded and not the complete json
        all_groups = fb_db.child("groups").child(self.id).shallow().get().val()
        logging.warning('%s - get_progress - downloaded all keys for groups from firebase' % self.id)

        # we will use a queue to limit the number of threads running in parallel
        q = Queue(maxsize=0)
        group_progress_list = []

        for group_id in all_groups:
            q.put([fb_db, group_progress_list, group_id])
        logging.warning('%s - get_progress - added all groups to queue' % self.id)

        logging.warning('%s - get_progress - setup threading with %s workers' % (self.id, num_threads))
        for i in range(num_threads):
            worker = threading.Thread(
                target=self.get_group_progress,
                args=(q,))
            worker.start()

        q.join()
        del fb_db
        logging.warning('%s - get_progress - downloaded progress for all groups from firebase' % self.id)

        # calculate project progress
        self.progress = np.average(group_progress_list, axis=0)[-1]
        logging.warning('%s - get_progress - calculated progress. progress = %s' % (self.id, self.progress))

        return group_progress_list

    def get_contributors(self, postgres):
        """
        The function to query the number of contributor for the project from the postgres database

        Parameters
        ----------
        postgres : database connection class
            The database connection to postgres database

        Returns
        -------
        contributors : int
            The number of users who contributed to this project
        """

        # establish postgres connection
        p_con = postgres()
        # sql command
        sql_query = '''
                SELECT
                  count(distinct(user_id))
                FROM
                  results
                WHERE
                  project_id = %s
            '''
        data = [self.id]
        # one row with one value will be returned
        self.contributors = p_con.retr_query(sql_query, data)[0][0]
        # delete/close db connection
        del p_con

        logging.warning("%s - get_contributors - got project contributors from postgres. contributors =  %s" % (self.id, self.contributors))

    def set_progress(self, firebase):
        """
        The function to set the progress in percent in firebase.

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
        # progress will be displayed as integer in the app
        fb_db.child("projects").child(self.id).update({"progress": int(self.progress)})

        logging.warning('%s - set_progress - set progress in firebase' % self.id)
        return True

    def set_contributors(self, firebase):
        """
        The function to set the number of contributors in firebase.

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication

        Returns
        -------
        bool
            True if successful. False otherwise.
        """

        fb_db = firebase.database()
        fb_db.child("projects").child(self.id).update({"contributors": self.contributors})

        logging.warning('%s - set_contributors - set contributors in firebase' % self.id)
        return True

    def set_project_progress_postgres(self, postgres)-> bool:
        """
        The function insert id, contributors, progress and timestamp into postgres progress relation

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
        sql_insert = '''
            INSERT INTO
              progress
            VALUES
              (%s,%s,%s,%s);
            '''
        timestamp = int(time.time())
        data = [self.id, self.contributors,
                self.progress, timestamp]

        p_con.query(sql_insert, data)
        logging.warning('%s - set_project_progress_postgres - inserted new entry for contributors and progress in progress relation' % self.id)
        del p_con

        return True

    ####################################################################################################################
    # EXPORT - We define a bunch of functions related to exporting exiting projects                                    #
    ####################################################################################################################
    def export_progress(self):
        """
        The function to log the progress to a txt file in the format 'progress_{ID}.txt'

        Returns
        -------
        bool
            True if successful, False otherwise.

        Notes
        -----
        The generated txt file will consist of a single line per log.
        We log a unix timestamp and the progress separated by comma
        """


        # check if output path for projects is correct and existing
        if not os.path.exists(DATA_PATH + '/progress'):
            os.makedirs(DATA_PATH + '/progress')

        filename = "{}/progress/progress_{}.json".format(DATA_PATH, self.id)

        # json already exists
        if os.path.isfile(filename):
            with open(filename, 'r') as input_file:
                progress_dict = json.load(input_file)
                # remove file
            os.remove(filename)
        # create new empty dict
        else:
            progress_dict = {
                "timestamps": [],
                "progress": [],
                "contributors": []
            }

        progress_dict['timestamps'].append(int(time.time()))
        progress_dict['progress'].append(self.progress)
        progress_dict['contributors'].append(self.contributors)
        # write file
        with open(filename, 'w') as output_file:
            json.dump(progress_dict, output_file, indent=4)


        logging.warning('%s - export_progress - exported progress to file: %s' % (self.id, filename))
        return True

    def export_results(self, postgres: object)-> bool:
        """
            TODO implement aggregate results per project type
            The function save the results of the project in a list of jsons'

            Parameters
            ----------
            postgres : object

            Returns
            -------

        """

        # this function is set concerning the project type
        results_list = self.aggregate_results(postgres)

        # check if output path for results is existing
        if not os.path.exists(DATA_PATH + '/results'):
            os.makedirs(DATA_PATH + '/results')
        
        output_json_file = '{}/results/results_{}.json'.format(DATA_PATH, self.id)

        with open(output_json_file, 'w') as outfile:
            json.dump(results_list, outfile, indent=4)

        logging.warning('ALL - export_results - exported results file: %s' % output_json_file)
        return True

    ####################################################################################################################
    # ARCHIVE - We define a bunch of functions related to archiving exiting projects                                   #
    ####################################################################################################################
    def archive_project(self, firebase, postgres):
        """
        The function to archives all project related information in firebase
            This includes information on groups

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        postgres : database connection class
            The database connection to postgres database

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        logging.warning('%s - archive_project - start archiving project' % self.id)
        self.archive_groups_firebase(firebase)
        self.archive_project_firebase(firebase)
        self.archive_project_postgres(postgres)
        logging.warning('%s - archive_project - finished archive project' % self.id)
        return True
