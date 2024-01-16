import csv
import datetime as dt
import json
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Dict, List

from osgeo import ogr

from mapswipe_workers import auth
from mapswipe_workers.definitions import DATA_PATH, CustomError, logger, sentry
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.utils import geojson_functions


@dataclass
class BaseTask:
    projectId: str
    groupId: str
    taskId: str


@dataclass
class BaseGroup:
    projectId: str
    groupId: str
    # TODO: attributes below could have default, but breaks inheritance.
    # After upgrading to Python 3.10 use kw_only=true and use defaults
    numberOfTasks: int  # TODO: can not be zero
    progress: int
    finishedCount: int
    requiredCount: int


class BaseProject(ABC):
    def __init__(self, project_draft):
        # TODO define as abstract base attributes
        self.groups: Dict[str, BaseGroup]
        self.tasks: Dict[str, List[BaseTask]]  # dict keys are group ids

        self.contributorCount = 0
        self.created = dt.datetime.now()
        self.createdBy = project_draft["createdBy"]
        self.groupMaxSize = project_draft.get("groupMaxSize", 0)
        self.groupSize = project_draft["groupSize"]
        self.image = project_draft["image"]  # Header image
        self.isFeatured = False
        self.lookFor = project_draft["lookFor"]  # Objects of interest
        self.name = project_draft["name"]
        self.progress = 0
        self.projectDetails = project_draft["projectDetails"]
        self.projectId = project_draft["projectDraftId"]
        self.projectNumber = project_draft.get("projectNumber", None)
        self.projectRegion = project_draft.get("projectRegion", None)
        self.projectTopic = project_draft.get("projectTopic", None)
        self.projectType = int(project_draft["projectType"])
        self.requestingOrganisation = project_draft.get("requestingOrganisation", None)
        self.requiredResults = 0
        self.resultCount = 0
        self.teamId = project_draft.get("teamId", None)
        # The number of users required for each task to be finished
        self.verificationNumber = project_draft["verificationNumber"]
        max_tasks_per_user = project_draft.get("maxTasksPerUser", None)
        if max_tasks_per_user is not None:
            self.maxTasksPerUser = int(max_tasks_per_user)

        if not self.teamId:
            self.status = "inactive"  # this is a public project
        else:
            self.status = (
                "private_inactive"  # private project visible only for team members
            )

        self.tutorialId = project_draft.get("tutorialId", None)
        # XXX: Additional fields (Used in manager dashboard for now)
        self.informationPages = project_draft.get("informationPages", None)
        self.customOptions = project_draft.get("customOptions", None)

        # currently crowdmap specific attributes
        # todo: discuss in group if empty attributes in mapswipe postgres are ok
        self.language = project_draft.get("language", "en-us")
        app_id = project_draft.get("appId", None)
        if app_id is not None:
            self.appId = int(app_id)
        self.manualUrl = project_draft.get("manualUrl", None)

    # TODO: Implement resultRequiredCounter as property.
    # Does not work because for some reason project['group'] = vars()
    # and then del project['group'] will delete also project.group.
    # @property
    # def resultRequiredCounter(self):
    #     return self.resultRequiredCounter

    def save_project(self):
        """
        Save all project info with groups and tasks
        in firebase and postgres.

        Returns
        ------
            Boolean: True = Successful
        """
        logger.info(f"{self.projectId}" f" - start creating a project")

        # Convert object attributes to dictionaries
        # for saving it to firebase and postgres
        tasks = {k: [asdict(i) for i in v] for k, v in self.tasks.items()}
        groups = {k: asdict(v) for k, v in self.groups.items()}
        project = vars(self)

        project.pop("groups")
        project.pop("tasks")
        project.pop("inputGeometries", None)
        project.pop("inputGeometriesFileName", None)

        # Convert Date object to ISO Datetime:
        # https://www.w3.org/TR/NOTE-datetime
        project["created"] = self.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        try:
            self.save_to_postgres(
                project,
                groups,
                tasks,
            )
            logger.info(
                f"{self.projectId}" f" - the project has been saved" f" to postgres"
            )
        except Exception as e:
            logger.exception(
                f"{self.projectId}"
                f" - the project could not be saved"
                f" to postgres and will therefor not be "
                f" saved to firebase"
            )
            raise CustomError(e)

        # if project can't be saved to files, delete also in postgres
        try:
            self.save_to_files(project)
            logger.info(
                f"{self.projectId}" f" - the project has been saved" f" to files"
            )
        except Exception as e:
            self.delete_from_postgres(self.projectId)
            logger.exception(
                f"{self.projectId}" f" - the project could not be saved" f" to files. "
            )
            logger.info(
                f"{self.projectId} deleted project data from files and postgres"
            )
            raise CustomError(e)

        try:
            self.save_project_to_firebase(project)
            self.save_groups_to_firebase(project["projectId"], groups)
            self.save_tasks_to_firebase(project["projectId"], tasks)
            # Delete project draft in Firebase once all things are in Firebase
            self.delete_draft_from_firebase()

            logger.info(
                f"{self.projectId}" f" - the project has been saved" f" to firebase"
            )
        # if project can't be saved to firebase, delete also in postgres
        except Exception as e:
            self.delete_draft_from_firebase()
            self.delete_from_postgres(self.projectId)
            self.delete_from_files()
            logger.exception(
                f"{self.projectId}"
                f" - the project could not be saved"
                f" to firebase. "
            )

            logger.info(
                f"{self.projectId} deleted project data from postgres and files"
            )
            raise CustomError(e)

        return True

    def save_project_to_firebase(self, project):
        firebase = Firebase()
        firebase.save_project_to_firebase(project)

    def save_groups_to_firebase(self, projectId: str, groups: dict):
        firebase = Firebase()
        firebase.save_groups_to_firebase(projectId, groups)

    @abstractmethod
    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        pass

    def save_to_postgres(self, project, groups, groupsOfTasks):
        """
        Defines SQL queries and data for import a project into postgres.
        SQL queries will be executed as transaction.
        (Either every query will be executed or none)
        """

        query_insert_project = """
            INSERT INTO projects
            VALUES (
              %s  -- created
              ,%s  -- createdBy
              ,ST_Force2D(ST_GeomFromText(%s, 4326)) -- geometry
              ,%s  -- image
              ,%s  -- isFeatured
              ,%s  -- lookFor
              ,%s  -- name
              ,%s  -- progress
              ,%s  -- projectDetails
              ,%s  -- projectId
              ,%s  -- projectType
              ,%s  -- requiredResults
              ,%s  -- resultCount
              ,%s  -- status
              ,%s  -- verificationCount
              ,%s  -- projectTypeSpecifics
              ,%s  -- organizationName
            );
            """

        project_attributes = [
            "created",
            "createdBy",
            "geometry",
            "image",
            "isFeatured",
            "lookFor",
            "name",
            "progress",
            "projectDetails",
            "projectId",
            "projectType",
            "requiredResults",
            "resultCount",
            "status",
            "verificationNumber",
            "organizationName",
        ]

        project_type_specifics = dict()
        for key, value in project.items():
            if key not in project_attributes:
                project_type_specifics[key] = value

        data_project = [
            self.created,
            self.createdBy,
            project["geometry"],
            project["image"],
            project["isFeatured"],
            project["lookFor"],
            project["name"],
            project["progress"],
            project["projectDetails"],
            project["projectId"],
            project["projectType"],
            project["requiredResults"],
            project["resultCount"],
            project["status"],
            project["verificationNumber"],
            json.dumps(project_type_specifics),
            project["requestingOrganisation"],
        ]

        query_recreate_raw_groups = """
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
            """

        query_insert_raw_groups = """
            INSERT INTO groups (
              project_id,
              group_id,
              number_of_tasks,
              finished_count,
              required_count,
              progress,
              project_type_specifics
            )
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
            """

        query_recreate_raw_tasks = """
            DROP TABLE IF EXISTS raw_tasks CASCADE;
            CREATE TABLE raw_tasks (
                project_id varchar,
                group_id varchar,
                task_id varchar,
                geom varchar,
                project_type_specifics json
            );
            """

        query_insert_raw_tasks = """
            INSERT INTO tasks
            SELECT
              project_id,
              group_id,
              task_id,
              CASE
                WHEN geom='' THEN NULL
                ELSE ST_Force2D(ST_Multi(ST_GeomFromText(geom, 4326)))
              END geom,
              project_type_specifics
            FROM raw_tasks;
            DROP TABLE IF EXISTS raw_tasks CASCADE;
            """

        groups_txt_filename = self.create_groups_txt_file(groups)
        tasks_txt_filename = self.create_tasks_txt_file(groupsOfTasks)

        groups_columns = [
            "project_id",
            "group_id",
            "number_of_tasks",
            "finished_count",
            "required_count",
            "progress",
            "project_type_specifics",
        ]

        tasks_columns = [
            "project_id",
            "group_id",
            "task_id",
            "geom",
            "project_type_specifics",
        ]

        # execution of all SQL-Statements as transaction
        # (either every query gets executed or none)
        try:
            p_con = auth.postgresDB()
            p_con._db_cur = p_con._db_connection.cursor()
            p_con._db_cur.execute(query_insert_project, data_project)
            p_con._db_cur.execute(query_recreate_raw_groups, None)
            p_con._db_cur.execute(query_recreate_raw_tasks, None)
            with open(groups_txt_filename, "r") as groups_file:
                p_con._db_cur.copy_from(
                    groups_file, "raw_groups", columns=groups_columns
                )
            with open(tasks_txt_filename, "r") as tasks_file:
                p_con._db_cur.copy_from(tasks_file, "raw_tasks", columns=tasks_columns)
            p_con._db_cur.execute(query_insert_raw_groups, None)
            p_con._db_cur.execute(query_insert_raw_tasks, None)
            p_con._db_connection.commit()
            p_con._db_cur.close()
        except Exception:
            del p_con
            raise

        os.remove(groups_txt_filename)
        os.remove(tasks_txt_filename)

    def save_to_files(self, project):
        """Save the project extent geometry as a GeoJSON file."""

        outfile = os.path.join(
            DATA_PATH,
            "api",
            "project_geometries",
            "project_geom_{}.geojson".format(self.projectId),
        )
        wkt_geom = project["geometry"]
        geometries = [ogr.CreateGeometryFromWkt(wkt_geom)]
        geojson_functions.create_geojson_file(geometries, outfile)

    def delete_from_files(self):
        """Delete the project extent geometry file."""
        outfile = (
            f"{DATA_PATH}/project_geometries/project_geom_{self.projectId}.geojson"
        )
        try:
            os.remove(outfile)
        except FileNotFoundError:
            pass

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

        if not os.path.isdir("{}/tmp".format(DATA_PATH)):
            os.mkdir("{}/tmp".format(DATA_PATH))

        # create txt file with header for later
        # import with copy function into postgres
        groups_txt_filename = f"{DATA_PATH}/tmp/raw_groups_{self.projectId}.txt"
        groups_txt_file = open(groups_txt_filename, "w", newline="")
        fieldnames = (
            "project_id",
            "group_id",
            "number_of_tasks",
            "finished_count",
            "required_count",
            "progress",
            "project_type_specifics",
        )
        w = csv.DictWriter(
            groups_txt_file,
            fieldnames=fieldnames,
            delimiter="\t",
            quotechar="'",
        )

        for groupId, group in groups.items():
            try:
                output_dict = {
                    "project_id": self.projectId,
                    "group_id": groupId,
                    "number_of_tasks": group["numberOfTasks"],
                    "finished_count": group["finishedCount"],
                    "required_count": group["requiredCount"],
                    "progress": group["progress"],
                    "project_type_specifics": dict(),
                }

                # these common attributes don't need to be written
                # to the project_type_specifics since they are
                # already stored in separate columns
                common_attributes = [
                    "projectId",
                    "groupId",
                    "numberOfTasks",
                    "requiredCount",
                    "finishedCount",
                    "progress",
                ]

                for key in group.keys():
                    if key not in common_attributes:
                        output_dict["project_type_specifics"][key] = group[key]
                output_dict["project_type_specifics"] = json.dumps(
                    output_dict["project_type_specifics"]
                )

                w.writerow(output_dict)

            except Exception as e:
                logger.exception(
                    f"{self.projectId}"
                    f" - set_groups_postgres - "
                    f"groups missed critical information: {e}"
                )
                sentry.capture_exception()

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

        if not os.path.isdir("{}/tmp".format(DATA_PATH)):
            os.mkdir("{}/tmp".format(DATA_PATH))

        # save tasks in txt file
        tasks_txt_filename = f"{DATA_PATH}/tmp/raw_tasks_{self.projectId}.txt"
        tasks_txt_file = open(tasks_txt_filename, "w", newline="")

        fieldnames = (
            "project_id",
            "group_id",
            "task_id",
            "geom",
            "project_type_specifics",
        )
        w = csv.DictWriter(
            tasks_txt_file,
            fieldnames=fieldnames,
            delimiter="\t",
            quotechar="'",
        )

        for groupId, tasks in groupsOfTasks.items():
            for task in tasks:
                output_dict = {
                    "project_id": self.projectId,
                    "group_id": groupId,
                    "task_id": task["taskId"],
                    "geom": task["geometry"],
                    "project_type_specifics": dict(),
                }

                # these common attributes don't need to be written
                # to the project_type_specifics since they are
                # already stored in separate columns
                common_attributes = [
                    "projectId",
                    "groupId",
                    "taskId",
                    "geometry",
                    "geojson",
                ]

                for key in task.keys():
                    if key not in common_attributes:
                        output_dict["project_type_specifics"][key] = task[key]
                output_dict["project_type_specifics"] = json.dumps(
                    output_dict["project_type_specifics"]
                ).replace(
                    "'", ""
                )  # to prevent error: invalid token "'"

                w.writerow(output_dict)
        tasks_txt_file.close()
        return tasks_txt_filename

    def delete_draft_from_firebase(self):
        firebase = Firebase()
        firebase.delete_project_draft_from_firebase(self.projectId)

    @staticmethod
    def delete_mapping_session_results(project_id):
        p_con = auth.postgresDB()
        sql_query = """
            DELETE FROM mapping_sessions_results msr
            USING mapping_sessions ms
            WHERE ms.mapping_session_id = msr.mapping_session_id
                AND ms.project_id = %(project_id)s;
        """
        p_con.query(sql_query, {"project_id": project_id})

    @classmethod
    def delete_from_postgres(cls, project_id):
        p_con = auth.postgresDB()

        cls.delete_mapping_session_results(project_id)

        sql_query = """
            DELETE FROM mapping_sessions WHERE project_id = %(project_id)s;
            DELETE FROM tasks WHERE project_id = %(project_id)s;
            DELETE FROM groups WHERE project_id = %(project_id)s;
            """
        p_con.query(sql_query, {"project_id": project_id})

        # -- Table from django/apps/aggregated/models.py. Used to cache stats data
        # NOTE: Django doesn't support database-level CASCADE delete
        #  https://docs.djangoproject.com/en/4.1/ref/models/fields/#django.db.models.ForeignKey.on_delete
        for aggregated_table_name in [
            "aggregated_aggregateduserstatdata",
            "aggregated_aggregatedusergroupstatdata",
        ]:
            if p_con.table_exists(aggregated_table_name):
                sql_query = f"""
                    DELETE FROM {aggregated_table_name}
                    WHERE project_id = %(project_id)s;
                """
                p_con.query(sql_query, {"project_id": project_id})

        sql_query = """DELETE FROM projects WHERE project_id = %(project_id)s;"""
        p_con.query(sql_query, {"project_id": project_id})

        del p_con
        logger.info(
            f"{project_id} - " f"deleted project, groups and tasks " f"from postgres"
        )

    def calc_required_results(self):
        for group in self.groups.values():
            group.requiredCount = self.verificationNumber
            self.requiredResults += group.requiredCount * group.numberOfTasks

    @abstractmethod
    def validate_geometries(self):
        pass

    @abstractmethod
    def create_groups(self):
        pass

    @abstractmethod
    def create_tasks(self):
        pass

    @staticmethod
    @abstractmethod
    def results_to_postgres(results: dict, project_id: str, filter_mode: bool):
        """How to move the result data from firebase to postgres."""
        pass

    @staticmethod
    @abstractmethod
    def get_per_project_statistics(project_id, project_info):
        """How to aggregate the project results."""
        pass
