from dataclasses import asdict

from mapswipe_workers import auth
from mapswipe_workers.definitions import CustomError, logger
from mapswipe_workers.utils import gzip_str


class Firebase:
    def __init__(self):
        self.fb_db = auth.firebaseDB()
        self.ref = self.fb_db.reference("")

    def save_project_to_firebase(self, project):
        # if a geometry exists in projects we want to delete it.
        # This geometry is not used in clients.
        project.pop("geometry", None)
        # save project
        self.ref.update({f"v2/projects/{project['projectId']}": project})
        logger.info(
            f"{project['projectId']} -"
            f" uploaded project to firebase realtime database"
        )

    def save_groups_to_firebase(self, projectId, groups):

        # save groups
        self.ref.update({f"v2/groups/{projectId}": groups})
        logger.info(f"{projectId} -" f" uploaded groups to firebase realtime database")

    def save_tasks_to_firebase(self, projectId, groupsOfTasks, useCompression: bool):
        task_upload_dict = {}
        for group_counter, group_id in enumerate(groupsOfTasks.keys()):
            for i in range(0, len(groupsOfTasks[group_id])):
                groupsOfTasks[group_id][i].pop("geometry", None)

            tasks_list = groupsOfTasks[group_id]
            # for tasks of a building footprint project
            # we use compression to reduce storage size in firebase
            # since the tasks hold geometries their storage size
            # can get quite big otherwise
            if useCompression:
                # removing properties from each task and compress
                for task in tasks_list:
                    task.pop("properties", None)

                tasks_list = gzip_str.compress_tasks(tasks_list)

            task_upload_dict[f"v2/tasks/{projectId}/{group_id}"] = tasks_list

            # we upload tasks in batches of maximum 150 groups
            # this is to avoid the maximum write size limit in firebase
            if len(task_upload_dict) % 150 == 0 or (group_counter + 1) == len(
                groupsOfTasks
            ):
                self.ref.update(task_upload_dict)
                logger.info(
                    f"{projectId} -"
                    f" uploaded 150 groups with tasks to firebase realtime database"
                )
                task_upload_dict = {}

    def delete_project_draft_from_firebase(self, projectId):
        self.ref.update({f"v2/projectDrafts/{projectId}": {}})
        logger.info(
            f"{projectId} -" f" deleted project draft from firebase realtime database"
        )

    def save_tutorial_to_firebase(
        self, tutorial, groups, groupsOfTasks, useCompression: bool
    ):
        tasks = {k: [asdict(i) for i in v] for k, v in groupsOfTasks.items()}
        groups = {k: asdict(v) for k, v in groups.items()}

        tutorialDict = vars(tutorial)

        tutorialDict.pop("groups", None)
        tutorialDict.pop("tasks", None)
        tutorialDict.pop("raw_tasks", None)
        tutorialDict.pop("examplesFile", None)
        tutorialDict.pop("tutorial_tasks", None)

        if not tutorial.projectId or tutorial.projectId == "":
            raise CustomError(
                "Given argument resulted in invalid "
                "Firebase Realtime Database reference. "
                f"Project Id is invalid: {tutorial.projectId}"
            )

        if useCompression:
            # we compress tasks for footprint project type using gzip
            compressed_tasks = gzip_str.compress_tasks(groupsOfTasks)
            tasks = {"101": compressed_tasks}

        self.ref.update(
            {
                f"v2/projects/{tutorial.projectId}": tutorialDict,
            }
        )
        self.ref.update(
            {
                f"v2/groups/{tutorial.projectId}": [groups],
            }
        )
        self.ref.update(
            {
                f"v2/tasks/{tutorial.projectId}": tasks,
            }
        )

        logger.info(f"uploaded tutorial data to firebase for {tutorial.projectId}")

    def drop_tutorial_draft(self, tutorialDraftId: str):
        self.ref.update({f"v2/tutorialDrafts/{tutorialDraftId}": {}})
