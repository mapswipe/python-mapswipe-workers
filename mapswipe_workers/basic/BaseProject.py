import logging

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


    # info is a dictionary with information about the project
    def __init__(self, project_id):
        # set basic project information
        self.id = project_id


    def set_project_info(self, import_key, import_dict):
        # set basic information based on import_dict
        self.import_key = import_key
        self.name = import_dict['project']['name']
        self.image = import_dict['project']['image']
        self.look_for = import_dict['project']['lookFor']
        self.project_details = import_dict['project']['projectDetails']
        self.verification_count = import_dict['project']['verificationCount']

        # the following attributes are set regardless the imported information
        self.is_featured = False
        self.state = 3
        self.group_average = 0
        self.progress = 0
        self.contributors = 0


    ## We define a bunch of functions related to importing new projects
    def import_project(self, import_key, import_dict, firebase, mysqlDB):
        # set all attributes
        self.set_project_info(import_key, import_dict)

        # check import before starting the import
        if not self.valid_import(firebase, mysqlDB):

            print(self.valid_import(firebase, mysqlDB))
            logging.warning('import is invalid')
            return False

        try:
            logging.warning('start importing project %s' % self.id)
            self.create_groups()
            #self.set_groups_firebase(firebase)
            self.set_project_mysql(mysqlDB)
            self.set_project_firebase(firebase)
            self.set_import_complete(firebase)
            logging.warning('imported project %s' % self.id)
            return True
        except Exception as e:
            logging.warning('could not import project %s' % self.id)
            logging.warning(e)
            self.delete_project(firebase, mysqlDB)

    def valid_import(self, firebase, mysqlDB):
        """
        The function to check whether a project has already been imported or import information is not valid

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        mysqlDB : database connection class
            The database connection to mysql database

        Returns
        -------
        bool
            True if successful. False otherwise.

        """

        logging.warning('starting to check if import is valid for %s' % self.import_key)

        # check if project already exists in firebase
        if self.project_exists_firebase(firebase):
            print(self.project_exists_firebase(firebase))
            print('firebase')
            return False
        elif self.project_exists_mysql(mysqlDB):
            print('mysql')
            return False
        # check if project already exists in mysql
        else:
            return True

    def project_exists_firebase(self, firebase):
        """
        The function to check whether a project exists in firebase.

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication

        Returns
        -------
        bool
            True if project exists in firebase projects table. False otherwise
        """

        fb_db = firebase.database()
        project_data = fb_db.child("projects").child(self.id).shallow().get().val()

        if not project_data:
            logging.warning('not in firebase. project: %s' % self.id)
            return False
        else:
            logging.warning('exists in firebase. project: %s' % self.id)
            return True

    def project_exists_mysql(self, mysqlDB):
        """
        The function to check whether a project exists in mysql.

        Parameters
        ----------
        mysqlDB : database connection class
            The database connection to mysql database

        Returns
        -------
        bool
            True is project exists in mysql database. False otherwise.
        """

        m_con = mysqlDB()
        sql_query = '''
            SELECT
              *
            FROM
              projects
            WHERE
              project_id = %s
        '''

        data = [self.id]
        project_data = m_con.retr_query(sql_query, data)
        del m_con

        if not project_data:
            logging.warning('not in mysql database. project: %s' % self.id)
            return False
        else:
            logging.warning('exists in mysql database. project: %s' % self.id)
            return True



    def set_groups_firebase(self, firebase):
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

        # create a dictionary for uploading in firebase
        groups = {}
        for group_id, group in self.groups.items():
            groups[group_id] = group.to_dict()

        # upload groups in firebase
        fb_db = firebase.database()
        fb_db.child("groups").child(self.id).set(groups)
        logging.warning('uploaded groups in firebase for project %s' % self.id)

    def set_project_firebase(self, firebase):
        """
        The function to upload the project information to the firebase projects table

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication

        Returns
        -------
        bool
            True if successfull. False otherwise

        Notes
        -----
        We don't upload all information to firebase
        We need to be careful with spelling here
        We do this to avoid uploading groups, etc.
        """

        project = {
            "id": self.id,
            "projectType": self.project_type,
            "name": self.name,
            "image": self.image,
            "lookFor": self.look_for,
            "projectDetails": self.project_details,
            "verificationCount": self.verification_count,
            "importKey": self.import_key,
            "isFeature": self.is_featured,
            "state":  self.state,
            "groupAverage": self.group_average,
            "progress": self.progress,
            "contributors": self.contributors,
            "info": self.info
        }

        fb_db = firebase.database()
        fb_db.child("projects").child(project['id']).set(project)
        logging.warning('uploaded project in firebase for project %s' % self.id)
        return True


    def set_project_mysql(self, mysqlDB):
        """
        The function to create a project in mysql
        Parameters
        ----------
        mysqlDB : database connection class
            The database connection to mysql database

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        m_con = mysqlDB()
        sql_insert = "INSERT INTO projects Values(%s,%s,%s)"
        data = [int(self.id), self.look_for, self.name]
        # insert in table
        try:
            m_con.query(sql_insert, data)
        except Exception as e:
            del m_con
            raise

        logging.warning('inserted project info in mysql for project %s' % self.id)
        return True

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

        logging.warning('set import complete for import %s and project %s' % (self.import_key, self.id))
        return True

    # We define a bunch of functions related to deleting projects
    def delete_project(self, firebase, mysqlDB):
        """
        The function to delete all project related information in firebase and mysql
            This includes information on groups

        Parameters
        ----------
        firebase : pyrebase firebase object
            initialized firebase app with admin authentication
        mysqlDB : database connection class
            The database connection to mysql database

        Returns
        -------
        bool
            True if successful. False otherwise
        """

        logging.warning('start deleting project %s' % self.id)
        self.delete_groups_firebase(firebase)
        self.delete_project_firebase(firebase)
        self.delete_project_mysql(mysqlDB)
        logging.warning('deleted project %s' % self.id)
        return True

    def delete_groups_firebase(self, firebase):
        """
        The function to delete all groups of a project in firebase

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
        fb_db.child("groups").child(self.id).remove()
        logging.warning('deleted groups in firebase for project %s' % self.id)
        return

    def delete_project_firebase(self, firebase):
        """
        The function to delete the project entry in the firebase projects table

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
        fb_db.child("projects").child(self.id).remove()
        logging.warning('deleted project in firebase for project %s' % self.id)
        return True

    def delete_import_firebase(self, firebase):
        """
        The function to delete an import in firebase
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
        fb_db.child("imports").child(self.import_key).remove()

        logging.warning('deleted import in firebase for project %s' % self.import_key)
        return True

    def delete_project_mysql(self, mysqlDB):
        """
        The function to delete a project in the mysql projects table.

        Parameters
        ----------
        mysqlDB : database connection class
            The database connection to mysql database

        Returns
        -------
        bool
            True is successful. False otherwise.

        TODO:
        -----
        Handle exception:
            pymysql.err.InternalError: (1205, 'Lock wait timeout exceeded; try restarting transaction')
        """

        m_con = mysqlDB()
        sql_insert = "DELETE FROM projects WHERE project_id = %s"
        data = [int(self.id)]
        # insert in table
        m_con.query(sql_insert, data)
        del m_con

        logging.warning('deleted project info in mysql for project %s' % self.id)
        return True

    ## We define a bunch of functions related to updating existing projects
    def update_project(self, firebase, mysqlDB):
        self.get_progress(firebase)
        self.get_contributors(mysqlDB)
        self.set_progress(firebase)
        self.set_contributors(firebase)

    def get_progress(self, firebase):
        self.progress = 100
        print("got project progress from firebase")

    def get_contributors(self, mysqlDB):
        """
        The function to query the number of contributor for the project from the mysql database

        Parameters
        ----------
        mysqlDB : database connection class
            The database connection to mysql database

        Returns
        -------
        contributors : int
            The number of users who contributed to this project
        """

        # establish mysql connection
        m_con = mysqlDB()
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
        self.contributors = m_con.retr_query(sql_query, data)[0][0]
        # delete/close db connection
        del m_con

        logging.warning("got project contributors from mysql for project: %s" % self.id)
        return self.contributors

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
        fb_db.child("projects").child(self.id).update({"progress": self.progress})

        logging.warning('set progress in firebase for project: %s' % self.id)
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
        fb_db.child("projects").child(self.project_id).update({"contributors": self.contributors})

        logging.warning('set contributors in firebase for project: %s' % self.id)
        return True

    # We define a bunch of functions related to exporting exiting projects
    def export_groups_as_json(self):


        project_json = 'some json'
        print("exported project as json")
        return project_json

    def export_project_as_json(self):
        project_json = 'some json'
        print("exported project as json")
        return project_json