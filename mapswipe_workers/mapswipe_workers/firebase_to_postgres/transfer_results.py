import csv
from io import StringIO

import dateutil.parser
from mapswipe_workers import auth
from mapswipe_workers.definitions import logger, sentry
from mapswipe_workers.firebase_to_postgres import update_data


def transfer_results(project_ids: list = None) -> list:
    """Download results from firebase, save them to postgres and delete them in firebase."""

    # Firebase transaction function
    def transfer(current_results):
        if current_results is None:
            logger.info(f"{project_id}: No results in Firebase")
        else:
            results_user_id_list = get_user_ids_from_results(current_results)
            update_data.update_user_data(results_user_id_list)
            results_file = results_to_file(current_results, project_id)
            save_results_to_postgres(results_file)

    fb_db = auth.firebaseDB()

    if not project_ids:
        # get project_ids from existing results if no project ids specified
        project_ids = list(fb_db.reference("v2/results/").get(shallow=True))

    if not project_ids:
        logger.info(f"There are no results to transfer.")
        return []

    # get all project ids from postgres, we will only transfer results for projects we have there
    postgres_project_ids = get_projects_from_postgres()

    for project_id in project_ids:
        if project_id not in postgres_project_ids:
            logger.info(
                f"{project_id}: This project is not in postgres. We will not transfer results"
            )
            continue
        elif "tutorial" in project_id:
            logger.info(
                f"{project_id}: these are results for a tutorial. we will not transfer these"
            )
            continue

        logger.info(f"{project_id}: Start transfering results")

        results_ref = fb_db.reference(f"v2/results/{project_id}")
        truncate_temp_results()

        try:
            results_ref.transaction(transfer)
        except fb_db.TransactionError:
            logger.exception(
                f"{project_id}: Firebase transaction for transfering results failed to commit"
            )
            sentry.capture_exception()
            return []

        logger.info(f"{project_id}: Transfered results to postgres")

    return project_ids


def results_to_file(results: dict, project_id: str) -> StringIO:
    """
    Writes results to an in-memory file like object
    formatted as a csv using the buffer module (StringIO).
    This can be then used by the COPY statement of Postgres
    for a more efficient import of many results into the Postgres
    instance.

    Returns
    -------
    results_file: io.StingIO
        The results in an StringIO buffer.
    """
    # If csv file is a file object, it should be opened with newline=''

    results_file = StringIO("")

    w = csv.writer(results_file, delimiter="\t", quotechar="'")

    logger.info(
        f"Got %s groups for project {project_id} to transfer" % len(results.items())
    )
    for groupId, users in results.items():
        for userId, results in users.items():

            # check if all attributes are set, if not don't transfer the results for this group
            try:
                timestamp = results["timestamp"]
                start_time = results["startTime"]
                end_time = results["endTime"]
                results = results["results"]
            except KeyError:
                logger.exception()
                sentry.capture_exception()
                continue

            timestamp = dateutil.parser.parse(timestamp)
            start_time = dateutil.parser.parse(start_time)
            end_time = dateutil.parser.parse(end_time)

            if type(results) is dict:
                for taskId, result in results.items():
                    w.writerow(
                        [
                            project_id,
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
                                project_id,
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


def save_results_to_postgres(results_file: StringIO) -> None:
    """
    Saves results to a temporary table in postgres using the COPY Statement of Postgres
    for a more efficient import into the database.
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


def truncate_temp_results() -> None:
    p_con = auth.postgresDB()
    query_truncate_temp_results = """
                    TRUNCATE results_temp
                """
    p_con.query(query_truncate_temp_results)


def get_user_ids_from_results(results) -> list:
    """
    Get all users based on the ids provided in the results
    """

    user_ids = set([])
    for groupId, users in results.items():
        for userId, results in users.items():
            user_ids.add(userId)

    return user_ids


def get_projects_from_postgres() -> list:
    """
    Get the id of all projects in postgres
    """

    pg_db = auth.postgresDB()
    sql_query = """
        SELECT project_id from projects;
    """
    raw_ids = pg_db.retr_query(sql_query, None)
    project_ids = [i[0] for i in raw_ids]
    return project_ids
