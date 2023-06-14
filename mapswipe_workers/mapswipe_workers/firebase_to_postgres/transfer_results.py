import csv
import io
from typing import List

import dateutil.parser
import geojson
import psycopg2

from mapswipe_workers import auth
from mapswipe_workers.definitions import ProjectType, logger, sentry
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
    # We will only transfer results for projects we have in postgres.
    project_type_per_id = get_projects_from_postgres()

    project_id_list_transfered = []
    for project_id in project_id_list:
        if project_id not in project_type_per_id.keys():
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
            project = ProjectType(project_type_per_id[project_id]).constructor

            transfer_results_for_project(project_id, results, project)
            project_id_list_transfered.append(project_id)

    return project_id_list_transfered


def transfer_results_for_project(
    project_id, results, project, filter_mode: bool = False
):
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
        results_user_group_id_list = list(
            set(
                [
                    user_group_id
                    for _, users in results.items()
                    for _, _results in users.items()
                    for user_group_id, is_selected in _results.get(
                        "userGroups", {}
                    ).items()
                    if is_selected
                ]
            )
        )
        update_data.update_user_data(results_user_id_list)
        if results_user_group_id_list:
            update_data.update_user_group_data(results_user_group_id_list)

    try:
        # Results are dumped into an in-memory file.
        # This allows us to use the COPY statement to insert many
        # results at relatively high speed.

        truncate_temp_user_groups_results()

        user_group_results_file = project.results_to_postgres(
            results, project_id, filter_mode=filter_mode
        )

        save_user_group_results_to_postgres(
            user_group_results_file, project_id, filter_mode=filter_mode
        )
    except psycopg2.errors.ForeignKeyViolation as e:
        # if we get here, we were in the middle of a transaction block
        # that failed because of a constraint trigger. To allow new commands
        # to be issued to postgres, we need to ROLLBACK first.
        p_con = auth.postgresDB()
        p_con.query("ROLLBACK")

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
            transfer_results_for_project(project_id, results, project, filter_mode=True)
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


def results_complete(result_data, projectId, groupId, userId, required_attributes):
    """check if all attributes are set"""
    complete = True
    for attribute in required_attributes:

        try:
            result_data[attribute]
        except KeyError as e:
            sentry.capture_exception(e)
            sentry.capture_message(
                f"missing attribute '{attribute}' for: "
                f"{projectId}/{groupId}/{userId}, will skip this one"
            )
            logger.exception(e)
            logger.warning(
                f"missing attribute '{attribute}' for: "
                f"{projectId}/{groupId}/{userId}, will skip this one"
            )
            complete = False
            continue
    return complete


def results_to_file(results, projectId, result_type: str = "integer"):
    """
    Writes results to an in-memory file like object
    formatted as a csv using the buffer module (StringIO).
    This can be then used by the COPY statement of Postgres
    for a more efficient import of many results into the Postgres
    instance.
    Parameters
    ----------
    results: dict
        The results as retrieved from the Firebase Realtime Database instance.
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

            # check if all attributes are set
            # if not don't transfer the results for this group
            if not results_complete(
                result_data,
                projectId,
                groupId,
                userId,
                required_attributes=["startTime", "endTime", "results"],
            ):
                continue

            user_group_ids = [
                user_group_id
                for user_group_id, is_selected in result_data.get(
                    "userGroups", {}
                ).items()
                if is_selected
            ]

            start_time = dateutil.parser.parse(result_data["startTime"])
            end_time = dateutil.parser.parse(result_data["endTime"])
            timestamp = end_time

            if type(result_data["results"]) is dict:
                for taskId, result in result_data["results"].items():
                    if result_type == "geometry":
                        result = geojson.dumps(geojson.GeometryCollection(result))
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
            elif type(result_data["results"]) is list:
                # TODO: optimize for performance
                # (make sure data from firebase is always a dict)
                # if key is a integer firebase will return a list
                # if first key (list index) is 5
                # list indicies 0-4 will have value None
                for taskId, result in enumerate(result_data["results"]):
                    if result is None:
                        continue
                    else:
                        if result_type == "geometry":
                            result = geojson.dumps(geojson.GeometryCollection(result))
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

            if result_data["results"]:
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


def save_results_to_postgres(
    results_file,
    project_id,
    filter_mode: bool,
    result_temp_table: str = "results_temp",
    result_table: str = "mapping_sessions_results",
):
    """
    Saves results to a temporary table in postgres
    using the COPY Statement of Postgres
    for a more efficient import into the database.
    Parameters
    ----------
    results_file: io.StringIO
    filter_mode: boolean
        If true, try to filter out invalid results.
    result_temp_table:
        result_temp_table and result_table are different from usual if
        result type is not int
    result_table:
        result_temp_table and result_table are different from usual if
        result type is not int
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
    p_con.copy_from(results_file, result_temp_table, columns)
    results_file.close()

    if filter_mode:
        logger.warning(f"trying to remove invalid tasks from {project_id}.")

        filter_query = f"""
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
                from {result_temp_table} r
                left join project_tasks t on
                    r.task_id = t.task_id and
                    r.group_id = t.group_id
                where t.task_id is null or t.group_id is null
            )
            delete from {result_temp_table} r1
            using results_to_delete r2
            where
                r1.task_id = r2.task_id and
                r1.group_id = r2.group_id and
                r1.user_id = r2.user_id
        """
        p_con.query(filter_query, {"project_id": project_id})

    # here we can handle different result types, e.g. convert Geojson to
    # native postgis geometry object
    if result_table == "mapping_sessions_results_geometry":
        # webapp saves coordinates as web-mercator
        result_sql = """
            ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(r.result), 3857), 4326) as result
        """
    else:
        result_sql = "r.result"

    query_insert_mapping_sessions = f"""
        BEGIN;
        INSERT INTO mapping_sessions
            SELECT
                project_id,
                group_id,
                user_id,
                nextval('mapping_sessions_mapping_session_id_seq'),
                min(start_time),
                max(end_time),
                count(*)
            FROM {result_temp_table}
            GROUP BY project_id, group_id, user_id
        ON CONFLICT (project_id,group_id,user_id)
        DO NOTHING;
        INSERT INTO {result_table}
            SELECT
                ms.mapping_session_id,
                r.task_id,
                {result_sql}
            FROM {result_temp_table} r
            JOIN mapping_sessions ms ON
                ms.project_id = r.project_id
                AND ms.group_id = r.group_id
                AND ms.user_id = r.user_id
        ON CONFLICT (mapping_session_id, task_id)
        DO NOTHING;
        COMMIT;
    """
    p_con.query(query_insert_mapping_sessions)
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
        logger.warning(f"trying to remove invalid tasks from {project_id}.")

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
        INSERT INTO mapping_sessions_user_groups
            SELECT
                ms.mapping_session_id,
                rug_temp.user_group_id
            FROM results_user_groups_temp rug_temp
                JOIN mapping_sessions ms USING (project_id, group_id, user_id)
        ON CONFLICT (mapping_session_id, user_group_id)
        DO NOTHING;
    """
    p_con.query(query_insert_results)
    del p_con
    logger.info("copied user_groups_results into postgres.")


def truncate_temp_results(temp_table: str = "results_temp"):
    p_con = auth.postgresDB()
    query_truncate_temp_results = f"TRUNCATE {temp_table};"
    p_con.query(query_truncate_temp_results)
    del p_con

    return


def truncate_temp_user_groups_results():
    p_con = auth.postgresDB()
    p_con.query("TRUNCATE results_user_groups_temp")
    del p_con
    return


def get_user_ids_from_results(results) -> List[str]:
    """
    Get all users based on the ids provided in the results
    """

    user_ids = set([])
    for _, users in results.items():
        for userId, results in users.items():
            user_ids.add(userId)

    return list(user_ids)


def get_projects_from_postgres() -> dict:
    """
    Get the id of all projects in postgres
    """

    pg_db = auth.postgresDB()
    sql_query = """
        SELECT project_id, project_type from projects;
    """
    result = pg_db.retr_query(sql_query, None)
    # todo: test query
    project_type_per_id = {}
    for _id, project_type in result:
        project_type_per_id[_id] = project_type

    del pg_db
    return project_type_per_id
