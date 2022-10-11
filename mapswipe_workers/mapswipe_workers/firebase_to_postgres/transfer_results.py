import csv
import io

import dateutil.parser
import psycopg2

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger, sentry
from mapswipe_workers.firebase_to_postgres import update_data


def transfer_results(project_id_list=None):
    """Transfer results for one project after the other.
    Will only trigger the transfer of results for projects
    that are defined in the postgres database.
    Will not transfer results for tutorials and
    for projects which are not set up in postgres.
    """
    if project_id_list is None:
        # get project_ids from existing results if no project ids specified
        fb_db = auth.firebaseDB()
        project_id_list = fb_db.reference("v2/results/").get(shallow=True)
        if project_id_list is None:
            project_id_list = []
            logger.info("There are no results to transfer.")

    # Get all project ids from postgres.
    # We will only transfer results for projects we in postgres.
    postgres_project_ids = get_projects_from_postgres()

    project_id_list_transfered = []
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
        else:
            logger.info(f"{project_id}: Start transfer results")
            fb_db = auth.firebaseDB()
            results_ref = fb_db.reference(f"v2/results/{project_id}")
            results = results_ref.get()
            del fb_db
            transfer_results_for_project(project_id, results)
            project_id_list_transfered.append(project_id)

    return project_id_list_transfered


def transfer_results_for_project(project_id, results, filter_mode: bool = False):
    """Transfer the results for a specific project.
    Save results into an in-memory file.
    Copy the results to postgres.
    Delete results in firebase.
    We are NOT using a Firebase transaction functions here anymore.
    This has caused problems, in situations where a lot of mappers are
    uploading results to Firebase at the same time. Basically, this is
    due to the behaviour of Firebase Transaction function:
        "If another client writes to this location
        before the new value is successfully saved,
        the update function is called again with the new current value,
        and the write will be retried."
    (source: https://firebase.google.com/docs/reference/admin/python/firebase_admin.db#firebase_admin.db.Reference.transaction)  # noqa
    Using Firebase transaction on the group level
    has turned out to be too slow when using "normal" queries,
    e.g. without using threading. Threading should be avoided here
    as well to not run into unforeseen errors.
    For more details see issue #478.
    """

    if results is None:
        logger.info(f"{project_id}: No results in Firebase")
    else:
        # First we check for new users in Firebase.
        # The user_id is used as a key in the postgres database for the results
        # and thus users need to be inserted before results get inserted.
        results_user_id_list = get_user_ids_from_results(results)
        results_user_group_id_list = set(
            [
                user_group_id
                for _, users in results.items()
                for _, results in users.items()
                for user_group_id, is_selected in results.get("userGroups", {}).items()
                if is_selected
            ]
        )
        update_data.update_user_data(results_user_id_list)
        if results_user_group_id_list:
            update_data.update_user_group_data(results_user_group_id_list)

    try:
        # Results are dumped into an in-memory file.
        # This allows us to use the COPY statement to insert many
        # results at relatively high speed.
        results_file, user_group_results_file = results_to_file(results, project_id)
        truncate_temp_results()
        truncate_temp_user_groups_results()
        save_results_to_postgres(results_file, project_id, filter_mode=filter_mode)
        save_user_group_results_to_postgres(
            user_group_results_file, project_id, filter_mode=filter_mode
        )
    except psycopg2.errors.ForeignKeyViolation as e:

        sentry.capture_exception(e)
        sentry.capture_message(
            "could not transfer results to postgres due to ForeignKeyViolation: "
            f"{project_id}; filter_mode={filter_mode}"
        )
        logger.exception(e)
        logger.warning(
            "could not transfer results to postgres due to ForeignKeyViolation: "
            f"{project_id}; filter_mode={filter_mode}"
        )

        # There is an exception where additional invalid tasks are in a group.
        # If that happens we arrive here and add the flag filtermode=true
        # to this function, which could solve the issue in save_results_to_postgres.
        # If it does not solve the issue we arrive again but
        # since filtermode is already true, we will not try to transfer results again.
        if not filter_mode:
            transfer_results_for_project(project_id, results, filter_mode=True)
    except Exception as e:
        sentry.capture_exception(e)
        sentry.capture_message(f"could not transfer results to postgres: {project_id}")
        logger.exception(e)
        logger.warning(f"could not transfer results to postgres: {project_id}")
    else:
        # It is important here that we first insert results into postgres
        # and then delete these results from Firebase.
        # In case something goes wrong during the insert, results in Firebase
        # will not get deleted.
        delete_results_from_firebase(project_id, results)
        logger.info(f"{project_id}: Transferred results to postgres")


def delete_results_from_firebase(project_id, results):
    """Delete results from Firebase using update function.
    We use the update method of firebase instead of delete.
    Update allows to delete items at multiple locations at the same time
    and is much faster.
    """

    fb_db = auth.firebaseDB()

    # we will use a multi-location update to delete the entries
    # therefore we create a dict with the items we want to delete
    data = {}
    for group_id, users in results.items():
        for user_id, result in users.items():
            key = f"{group_id}/{user_id}"
            data[key] = None

    results_ref = fb_db.reference(f"v2/results/{project_id}/")
    results_ref.update(data)

    logger.info(f"removed results for project {project_id}")


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
    user_group_results_file = io.StringIO("")

    w = csv.writer(results_file, delimiter="\t", quotechar="'")
    user_group_results_csv = csv.writer(
        user_group_results_file, delimiter="\t", quotechar="'"
    )

    logger.info(f"Got {len(results.items())} groups for project {projectId}")
    for groupId, users in results.items():
        for userId, result_data in users.items():

            # check if all attributes are set,
            # if not don't transfer the results for this group
            try:
                start_time = result_data["startTime"]
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
                end_time = result_data["endTime"]
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
                result_results = result_data["results"]
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

            user_group_ids = [
                user_group_id
                for user_group_id, is_selected in result_data.get(
                    "userGroups", {}
                ).items()
                if is_selected
            ]
            start_time = dateutil.parser.parse(start_time)
            end_time = dateutil.parser.parse(end_time)
            timestamp = end_time
            results_added = False

            if type(result_results) is dict:
                if result_results:
                    results_added = True
                for taskId, result in result_results.items():
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
            elif type(result_results) is list:
                # TODO: optimize for performance
                # (make sure data from firebase is always a dict)
                # if key is a integer firebase will return a list
                # if first key (list index) is 5
                # list indicies 0-4 will have value None
                if result_results:
                    results_added = True
                for taskId, result in enumerate(result_results):
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

            if results_added:
                user_group_results_csv.writerows(
                    [
                        [
                            # Not using taskId as it is included by projectId-groupId
                            projectId,
                            groupId,
                            userId,
                            user_group_id,
                        ]
                        for user_group_id in user_group_ids
                    ]
                )

    results_file.seek(0)
    user_group_results_file.seek(0)
    return results_file, user_group_results_file


def save_results_to_postgres(results_file, project_id, filter_mode: bool):
    """
    Saves results to a temporary table in postgres
    using the COPY Statement of Postgres
    for a more efficient import into the database.
    Parameters
    ----------
    results_file: io.StringIO
    filter_mode: boolean
        If true, try to filter out invalid results.
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

    if filter_mode:
        logger.warn(f"trying to remove invalid tasks from {project_id}.")

        filter_query = """
            with project_tasks as (
                select
                    task_id
                    ,group_id
                from tasks
                where project_id = %(project_id)s
            ),
            -- Results for which we can't join a task from the tasks table
            -- are invalid. For these invalid results the group_id set by the app
            -- is not correct. Hence, we delete these results from the
            -- results_temp table.
            results_to_delete as (
                select
                    r.task_id
                    ,r.group_id
                    ,r.user_id
                from results_temp r
                left join project_tasks t on
                    r.task_id = t.task_id and
                    r.group_id = t.group_id
                where t.task_id is null or t.group_id is null
            )
            delete from results_temp r1
            using results_to_delete r2
            where
                r1.task_id = r2.task_id and
                r1.group_id = r2.group_id and
                r1.user_id = r2.user_id
        """
        p_con.query(filter_query, {"project_id": project_id})

    query_insert_results = """
        INSERT INTO results
            SELECT * FROM results_temp
        ON CONFLICT (project_id,group_id,user_id,task_id)
        DO NOTHING;
    """
    p_con.query(query_insert_results)
    del p_con
    logger.info("copied results into postgres.")


def save_user_group_results_to_postgres(
    user_group_results_file,
    project_id,
    filter_mode: bool,
):
    """
    Saves results to a temporary table in postgres
    using the COPY Statement of Postgres
    for a more efficient import into the database.
    Parameters
    ----------
    user_group_results_file: io.StringIO
    filter_mode: boolean
        If true, try to filter out invalid results.
    """

    p_con = auth.postgresDB()
    columns = [
        "project_id",
        "group_id",
        "user_id",
        "user_group_id",
    ]
    user_group_results_file.seek(0)
    p_con.copy_from(user_group_results_file, "results_user_groups_temp", columns)
    user_group_results_file.close()

    if filter_mode:
        logger.warn(f"trying to remove invalid tasks from {project_id}.")

        filter_query = """
            WITH project_groups AS (
                SELECT
                    group_id
                FROM groups
                WHERE project_id = %(project_id)s
            ),
            -- Results for which we can't join a group from the groups table
            -- are invalid. For these invalid results the group_id set by the app
            -- is not correct. Hence, we delete these results from the
            -- results_user_groups_temp table.
            user_group_results_to_delete AS (
                SELECT
                    R.group_id,
                    R.user_id
                FROM results_user_groups_temp R
                    LEFT join project_groups T on R.group_id = T.group_id
                    LEFT join users U on R.user_id = U.user_id
                    LEFT join user_groups UG on R.user_group_id = UG.user_group_id
                WHERE T.group_id is NULL
                    OR U.user_id is NULL
                    OR UG.user_group_id is NULL
            )
            DELETE FROM results_user_groups_temp R1
            USING user_group_results_to_delete R2
            WHERE
                R1.group_id = R2.group_id
                AND R1.user_id = R2.user_id
        """
        p_con.query(filter_query, {"project_id": project_id})

    query_insert_results = """
        INSERT INTO results_user_groups
            SELECT * FROM results_user_groups_temp
        ON CONFLICT (project_id, group_id, user_id, user_group_id)
        DO NOTHING;
    """
    p_con.query(query_insert_results)
    del p_con
    logger.info("copied user_groups_results into postgres.")


def truncate_temp_results():
    p_con = auth.postgresDB()
    query_truncate_temp_results = """
                    TRUNCATE results_temp
                """
    p_con.query(query_truncate_temp_results)
    del p_con

    return


def truncate_temp_user_groups_results():
    p_con = auth.postgresDB()
    p_con.query("TRUNCATE results_user_groups_temp")
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
