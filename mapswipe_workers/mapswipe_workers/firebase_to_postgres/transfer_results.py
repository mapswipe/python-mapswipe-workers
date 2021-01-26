import csv
import io

import dateutil.parser
import pandas as pd

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger, sentry
from mapswipe_workers.firebase_to_postgres import update_data


def transfer_results(project_id_list=None):
    """
    Download results from firebase,
    saves them to postgres and then deletes the results in firebase.
    This is implemented as a transactional operation as described in
    the Firebase docs to avoid missing new generated results in
    Firebase during execution of this function.
    """

    # Firebase transaction function
    def transfer(current_results):
        if current_results is None:
            logger.info(f"{project_id}: No results in Firebase")
            return dict()
        else:
            results_user_id_list = get_user_ids_from_results(current_results)
            update_data.update_user_data(results_user_id_list)
            results_file = results_to_file(current_results, project_id)
            save_results_to_postgres(results_file)
            return dict()

    fb_db = auth.firebaseDB()

    if not project_id_list:
        # get project_ids from existing results if no project ids specified
        project_id_list = fb_db.reference("v2/results/").get(shallow=True)
        if not project_id_list:
            project_id_list = []
            logger.info("There are no results to transfer.")

    # get all project ids from postgres,
    # we will only transfer results for projects we have there
    postgres_project_ids = get_projects_from_postgres()

    for project_id in project_id_list:
        if project_id not in postgres_project_ids:
            logger.info(
                f"{project_id}: This project is not in postgres. "
                f"We will not transfer results"
            )
            continue
        elif "tutorial" in project_id:
            logger.info(
                f"{project_id}: these are results for a tutorial. "
                f"We will not transfer these"
            )
            continue

        logger.info(f"{project_id}: Start transfering results")

        results_ref = fb_db.reference(f"v2/results/{project_id}")
        truncate_temp_results()

        try:
            results_ref.transaction(transfer)
            logger.info(f"{project_id}: Transfered results to postgres")
        except fb_db.TransactionAbortedError:
            logger.exception(
                f"{project_id}: Firebase transaction for "
                f"transfering results failed to commit"
            )
            sentry.capture_exception()

    del fb_db
    return project_id_list


def results_to_file(results, projectId):
    """
    Writes results to an in-memory file like object
    formatted as a csv using the buffer module (StringIO).
    This can be then used by the COPY statement of Postgres
    for a more efficient import of many results into the Postgres
    instance.
    Parameters
    ----------
    results: dict
        The results as retrived from the Firebase Realtime Database instance.
    Returns
    -------
    results_file: io.StingIO
        The results in an StringIO buffer.
    """
    # If csv file is a file object, it should be opened with newline=''

    results_file = io.StringIO("")

    w = csv.writer(results_file, delimiter="\t", quotechar="'")

    logger.info(f"Got {len(results.items())} groups for project {projectId}")

    # check if the group id is set correct in the app
    # only do this for project '-MRL3frZWPOCR94ehFnp'
    if projectId == '-MRL3frZWPOCR94ehFnp':
        # get groups and tasks as dict for this project
        # this will be used later to check if the group is wrong
        pg_db = auth.postgresDB()
        sql_query = """
            SELECT group_id, task_id FROM tasks
            WHERE project_id = '-MRL3frZWPOCR94ehFnp'
        """
        wsf_tasks_table = pg_db.retr_query(sql_query, None)
        wsf_tasks_df = pd.DataFrame(wsf_tasks_table, columns=["group_id", "task_id"])

    for groupId, users in results.items():
        for userId, results in users.items():

            # check if all attributes are set,
            # if not don't transfer the results for this group
            try:
                start_time = results["startTime"]
            except KeyError as e:
                sentry.capture_exception(e)
                sentry.capture_message(
                    "missing attribute 'startTime' for: "
                    f"{projectId}/{groupId}/{userId}, will skip this one"
                )
                logger.exception(e)
                logger.warning(
                    "missing attribute 'startTime' for: "
                    f"{projectId}/{groupId}/{userId}, will skip this one"
                )
                continue

            try:
                end_time = results["endTime"]
            except KeyError as e:
                sentry.capture_exception(e)
                sentry.capture_message(
                    "missing attribute 'endTime' for: "
                    f"{projectId}/{groupId}/{userId}, will skip this one"
                )
                logger.exception(e)
                logger.warning(
                    "missing attribute 'endTime' for: "
                    f"{projectId}/{groupId}/{userId}, will skip this one"
                )
                continue

            try:
                results = results["results"]
            except KeyError as e:
                sentry.capture_exception(e)
                sentry.capture_message(
                    "missing attribute 'results' for: "
                    f"{projectId}/{groupId}/{userId}, will skip this one"
                )
                logger.exception(e)
                logger.warning(
                    "missing attribute 'results' for: "
                    f"{projectId}/{groupId}/{userId}, will skip this one"
                )
                continue

            start_time = dateutil.parser.parse(start_time)
            end_time = dateutil.parser.parse(end_time)
            timestamp = end_time

            if type(results) is dict:
                for taskId, result in results.items():
                    # check if the group id is set correct in the app
                    # only do this for project '-MRL3frZWPOCR94ehFnp'
                    if projectId == '-MRL3frZWPOCR94ehFnp':
                        group_id_db = wsf_tasks_df.loc[wsf_tasks_df['task_id'] == taskId]["group_id"]
                        # log the old and new group id
                        if group_id_db != groupId:
                            groupId = group_id_db
                        else:
                            pass

                    w.writerow(
                        [
                            projectId,
                            groupId,
                            userId,
                            taskId,
                            timestamp,
                            start_time,
                            end_time,
                            result,
                        ]
                    )
            elif type(results) is list:
                # TODO: optimize for performance
                # (make sure data from firebase is always a dict)
                # if key is a integer firebase will return a list
                # if first key (list index) is 5
                # list indicies 0-4 will have value None
                for taskId, result in enumerate(results):
                    if result is None:
                        continue
                    else:
                        w.writerow(
                            [
                                projectId,
                                groupId,
                                userId,
                                taskId,
                                timestamp,
                                start_time,
                                end_time,
                                result,
                            ]
                        )
            else:
                raise TypeError

    results_file.seek(0)
    return results_file


def save_results_to_postgres(results_file):
    """
    Saves results to a temporary table in postgres
    using the COPY Statement of Postgres
    for a more efficient import into the database.

    Parameters
    ----------
    results_file: io.StringIO
    """

    p_con = auth.postgresDB()
    columns = [
        "project_id",
        "group_id",
        "user_id",
        "task_id",
        "timestamp",
        "start_time",
        "end_time",
        "result",
    ]
    p_con.copy_from(results_file, "results_temp", columns)
    results_file.close()

    query_insert_results = """
        INSERT INTO results
            SELECT * FROM results_temp
        ON CONFLICT (project_id,group_id,user_id,task_id)
        DO NOTHING;
    """
    p_con.query(query_insert_results)
    del p_con


def truncate_temp_results():
    p_con = auth.postgresDB()
    query_truncate_temp_results = """
                    TRUNCATE results_temp
                """
    p_con.query(query_truncate_temp_results)
    del p_con

    return


def get_user_ids_from_results(results):
    """
    Get all users based on the ids provided in the results
    """

    user_ids = set([])
    for groupId, users in results.items():
        for userId, results in users.items():
            user_ids.add(userId)

    return user_ids


def get_projects_from_postgres():
    """
    Get the id of all projects in postgres
    """

    pg_db = auth.postgresDB()
    sql_query = """
        SELECT project_id from projects;
    """
    raw_ids = pg_db.retr_query(sql_query, None)
    project_ids = [i[0] for i in raw_ids]

    del pg_db
    return project_ids
