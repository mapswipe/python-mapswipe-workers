from abc import ABCMeta, abstractmethod
import csv
import datetime as dt
import json
import os
import sys

from mapswipe_workers import auth
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import logger


class BaseProject(metaclass=ABCMeta):
    """
    The base class for creating

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

    def __init__(self, project_draft):
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

        self.archived = False
        self.created = dt.datetime.now()
        self.createdBy = project_draft['createdBy']
        self.groups = list()
        self.groupMaxSize = project_draft.get('groupMaxSize', 0)
        self.resultCount = 0
        self.image = project_draft['image']
        self.isFeatured = False
        self.lookFor = project_draft['lookFor']
        self.name = project_draft['name']
        self.requiredResults = 0
        self.progress = 0
        self.projectDetails = project_draft['projectDetails']
        self.projectId = project_draft['projectDraftId']
        self.projectType = int(project_draft['projectType'])
        self.verificationNumber = project_draft['verificationNumber']
        self.status = 'new'

    # TODO: Implement resultRequiredCounter as property.
    # Does not work because for some reason project['group'] = vars()
    # and then del project['group'] will delete also project.group.
    # @property
    # def resultRequiredCounter(self):
    #     return self.resultRequiredCounter

    def save_project(self, fb_db):
        """
        Creates a projects with groups and tasks
        and saves it in firebase and postgres

        Returns
        ------
            Boolean: True = Successful
        """
        logger.info(
            f'{self.projectId}'
            f' - start creating a project'
            )

        # Convert object attributes to dictonaries
        # for saving it to firebase and postgres
        project = vars(self)
        groups = dict()
        groupsOfTasks = dict()
        for group in self.groups:
            group = vars(group)
            tasks = list()
            for task in group['tasks']:
                tasks.append(vars(task))
            groupsOfTasks[group['groupId']] = tasks
            del group['tasks']
            groups[group['groupId']] = group
        del(project['groups'])
        project.pop('inputGeometries', None)
        project.pop('validInputGeometries', None)
        # Convert Date object to ISO Datetime:
        # https://www.w3.org/TR/NOTE-datetime
        project['created'] = self.created.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        # logger.info(
        #         f'{self.projectId}'
        #         f' - size of all tasks: '
        #         f'{sys.getsizeof(json.dumps(groupsOfTasks))/1024/1024} MB'
        #         )
        # Make sure projects get saved in Postgres and Firebase successful
        try:
            self.save_to_postgres(
                    project,
                    groups,
                    groupsOfTasks,
                    )
            logger.info(
                    f'{self.projectId}'
                    f' - the project has been saved'
                    f' to postgres'
                    )
            try:
                self.save_to_firebase(
                        fb_db,
                        project,
                        groups,
                        groupsOfTasks,
                        )
                logger.info(
                        f'{self.projectId}'
                        f' - the project has been saved'
                        f' to firebase'
                        )
                return True
            except Exception:
                self.delete_from_postgres()
                logger.exception(
                        f'{self.projectId}'
                        f' - the project could not be saved'
                        f' to firebase. '
                        )
                return False
        except Exception:
            logger.exception(
                    f'{self.projectId}'
                    f' - the project could not be saved'
                    f' to postgres and will therefor not be '
                    f' saved to firebase'
                    )
            return False

    def save_to_firebase(self, fb_db, project, groups, groupsOfTasks):

        # remove wkt geometry attribute of projects and tasks
        project.pop('geometry', None)
        for group_id in groupsOfTasks.keys():
            for i in range(0, len(groupsOfTasks[group_id])):
                groupsOfTasks[group_id][i].pop('geometry', None)


        ref = fb_db.reference('')
        ref.update({
            f'v2/projects/{self.projectId}': project,
            f'v2/groups/{self.projectId}': groups,
            f'v2/tasks/{self.projectId}': groupsOfTasks,
            })
        logger.info(
                f'{self.projectId} -'
                f' uploaded project, groups and'
                f' tasks to firebase realtime database'
                )
        ref = fb_db.reference(f'v2/projectDrafts/{self.projectId}')
        ref.set({})

    def save_to_postgres(self, project, groups, groupsOfTasks):
        '''
        Defines SQL queries and data for import a project into postgres.
        SQL queries will be executed as transaction.
        (Either every query will be executed or none)
        '''

        query_insert_project = '''
            INSERT INTO projects
            VALUES (%s,%s,%s,ST_Force2D(ST_Multi(ST_GeomFromText(%s, 4326))),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            '''

        data_project = [
                project['archived'],
                self.created,
                self.createdBy,
                project['geometry'],
                project['image'],
                project['isFeatured'],
                project['lookFor'],
                project['name'],
                project['progress'],
                project['projectDetails'],
                project['projectId'],
                project['projectType'],
                project['requiredResults'],
                project['resultCount'],
                project['status'],
                project['verificationNumber']
        ]

        project_attributes = [
                'archived',
                'created',
                'createdBy',
                'geometry',
                'image',
                'isFeatured',
                'lookFor',
                'name',
                'progress',
                'projectDetails',
                'projectId',
                'projectType',
                'requiredResults',
                'resultCount',
                'status',
                'verificationNumber'
                ]

        project_type_specifics = dict()
        for key, value in project.items():
            if key not in project_attributes:
                project_type_specifics[key] = value
        data_project.append(json.dumps(project_type_specifics))

        query_recreate_raw_groups = '''
            DROP TABLE IF EXISTS raw_groups CASCADE;
            CREATE TABLE raw_groups (
              project_id varchar,
              group_id varchar,
              number_of_tasks int,
              finished_count int,
              required_count int,
              progress int,
              project_type_specifics json
            );
            '''

        query_insert_raw_groups = '''
            INSERT INTO groups
            SELECT
              project_id,
              group_id,
              number_of_tasks,
              finished_count,
              required_count,
              progress,
              project_type_specifics
            FROM raw_groups;
            DROP TABLE IF EXISTS raw_groups CASCADE;
            '''

        query_recreate_raw_tasks = '''
            DROP TABLE IF EXISTS raw_tasks CASCADE;
            CREATE TABLE raw_tasks (
                project_id varchar,
                group_id varchar,
                task_id varchar,
                geom varchar,
                project_type_specifics json
            );
            '''

        query_insert_raw_tasks = '''
            INSERT INTO tasks
            SELECT
              project_id,
              group_id,
              task_id,
              ST_Force2D(ST_Multi(ST_GeomFromText(geom, 4326))),
              project_type_specifics
            FROM raw_tasks;
            DROP TABLE IF EXISTS raw_tasks CASCADE;
            '''

        groups_txt_filename = self.create_groups_txt_file(groups)
        tasks_txt_filename = self.create_tasks_txt_file(groupsOfTasks)

        groups_columns = [
                'project_id',
                'group_id',
                'number_of_tasks',
                'finished_count',
                'required_count',
                'progress',
                'project_type_specifics'
                ]

        tasks_columns = [
                'project_id',
                'group_id',
                'task_id',
                'geom',
                'project_type_specifics']

        # execution of all SQL-Statements as transaction
        # (either every query gets executed or none)
        try:
            p_con = auth.postgresDB()
            p_con._db_cur = p_con._db_connection.cursor()
            p_con._db_cur.execute(query_insert_project, data_project)
            p_con._db_cur.execute(query_recreate_raw_groups, None)
            p_con._db_cur.execute(query_recreate_raw_tasks, None)
            with open(groups_txt_filename, 'r') as groups_file:
                p_con._db_cur.copy_from(
                        groups_file,
                        'raw_groups',
                        columns=groups_columns
                        )
            with open(tasks_txt_filename, 'r') as tasks_file:
                p_con._db_cur.copy_from(
                        tasks_file,
                        'raw_tasks',
                        columns=tasks_columns
                        )
            p_con._db_cur.execute(query_insert_raw_groups, None)
            p_con._db_cur.execute(query_insert_raw_tasks, None)
            p_con._db_connection.commit()
            p_con._db_cur.close()
        except Exception:
            del p_con
            raise

        os.remove(groups_txt_filename)
        os.remove(tasks_txt_filename)

    def create_groups_txt_file(self, groups):
        """
        Creates a text file containing groups information
        for a specific project.
        The text file is temporary and used only by BaseImport module.

        Parameters
        ----------
        projectId : int
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

        # create txt file with header for later
        # import with copy function into postgres
        groups_txt_filename = (
                f'{DATA_PATH}/tmp/raw_groups_{self.projectId}.txt'
                )
        groups_txt_file = open(groups_txt_filename, 'w', newline='')
        fieldnames = (
                'project_id',
                'group_id',
                'number_of_tasks',
                'finished_count',
                'required_count',
                'progress',
                'project_type_specifics'
                )
        w = csv.DictWriter(
                groups_txt_file,
                fieldnames=fieldnames,
                delimiter='\t',
                quotechar="'",
                )

        for groupId, group in groups.items():
            try:
                output_dict = {
                    "project_id": self.projectId,
                    "group_id": groupId,
                    "number_of_tasks": group['numberOfTasks'],
                    "finished_count": group['finishedCount'],
                    "required_count": group['requiredCount'],
                    "progress": group['progress'],
                    "project_type_specifics": dict()
                }

                for key in group.keys():
                    if key not in output_dict.keys():
                        output_dict['project_type_specifics'][key] = group[key]
                output_dict['project_type_specifics'] = json.dumps(
                        output_dict['project_type_specifics']
                        )

                w.writerow(output_dict)

            except Exception as e:
                logger.exception(
                        f'{self.projectId}'
                        f' - set_groups_postgres - '
                        f'groups missed critical information: {e}'
                        )

        groups_txt_file.close()

        return groups_txt_filename

    def create_tasks_txt_file(self, groupsOfTasks):
        """
        Creates a text file containing tasks information
        for a specific project.
        It interates over groups and extracts tasks.
        The text file is temporary and used only by BaseImport module.

        Parameters
        ----------
        projectId : int
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
        tasks_txt_filename = f'{DATA_PATH}/tmp/raw_tasks_{self.projectId}.txt'
        tasks_txt_file = open(tasks_txt_filename, 'w', newline='')

        fieldnames = (
                'project_id',
                'group_id',
                'task_id',
                'geom',
                'project_type_specifics'
                )
        w = csv.DictWriter(
                tasks_txt_file,
                fieldnames=fieldnames,
                delimiter='\t',
                quotechar="'",
                )

        for groupId, tasks in groupsOfTasks.items():
            for task in tasks:
                output_dict = {
                        "project_id": self.projectId,
                        "group_id": groupId,
                        "task_id": task['taskId'],
                        "geom": task['geometry'],
                        "project_type_specifics": dict()
                        }
                for key in task.keys():
                    if key not in output_dict.keys():
                        output_dict['project_type_specifics'][key] = task[key]
                output_dict['project_type_specifics'] = json.dumps(
                        output_dict['project_type_specifics']
                        )

                w.writerow(output_dict)
        tasks_txt_file.close()
        return tasks_txt_filename

    def delete_from_postgres(self):
        p_con = auth.postgresDB()

        sql_query = '''
            DELETE FROM tasks WHERE project_id = %s;
            DELETE FROM groups WHERE project_id = %s;
            DELETE FROM projects WHERE project_id = %s;
            '''
        data = [
            self.projectId,
            self.projectId,
            self.projectId,
        ]
        p_con.query(sql_query, data)
        del p_con
        logger.info(
                f'{self.projectId} - '
                f'deleted project, groups and tasks '
                f'from postgres'
                )

    def calc_required_results(self):
        for group in self.groups:
            group.requiredCount = self.verificationNumber
            self.requiredResults = (
                    self.requiredResults +
                    group.requiredCount *
                    group.numberOfTasks
                    )

    def get_tile_server(self, tile_server):
        '''
        Creates a dictonary with informations of the tile server
        with project draft values or default values.
        '''

        name = tile_server.get('name', 'bing')

        url = tile_server.get('url', auth.get_tileserver_url(tile_server.get('name', 'bing')))
        if url == '':
            url = auth.get_tileserver_url(tile_server.get('name', 'bing'))

        apiKeyRequired = tile_server.get('apiKeyRequired')

        apiKey = tile_server.get('apiKey', auth.get_api_key(tile_server.get('name', 'bing')))
        if apiKey == '':
            apiKey = auth.get_api_key(tile_server.get('name', 'bing'))

        wmtsLayerName = tile_server.get('wmtsLayerName', None)
        if wmtsLayerName == '':
            wmtsLayerName = None

        captions = tile_server.get('caption', None)

        date = tile_server.get('date', None)

        credits = tile_server.get('credits', '')

        tile_server_dict = {
            'name': name,
            'url': url,
            'apiKeyRequired': apiKeyRequired,
            'apiKey': apiKey,
            'wmtsLayerName': wmtsLayerName,
            'captions': captions,
            'date': date,
            'credits': credits
        }

        return tile_server_dict

    @abstractmethod
    def validate_geometries():
        pass

    @abstractmethod
    def create_groups():
        pass
