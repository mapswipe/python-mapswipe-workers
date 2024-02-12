"""Update users and project information from Firebase in Postgres."""

import concurrent.futures
import csv
import datetime as dt
import io
from typing import List, Optional
from google.auth.exceptions import TransportError

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


# TODO: Change firebase/client side to send UTC time instead.
def convert_timestamp_to_database_format(timestamp_number):
    if timestamp_number:
        return dt.datetime.fromtimestamp(timestamp_number / 1000).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )


def convert_firebase_datetime_to_database_format(timestamp):
    if timestamp:
        return dt.datetime.strptime(timestamp.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")


def get_user_attribute_from_firebase(user_ids: List[str], attribute: str):
    """Use threading to query a user attribute in firebase.

    Follows a workflow describted in this blogpost:
    https://www.digitalocean.com/community/tutorials/how-to-use-threadpoolexecutor-in-python-3
    """

    def get_user_attribute(_user_id, _attribute):
        ref = fb_db.reference(f"v2/users/{_user_id}/{_attribute}")
        return [_user_id, ref.get()]

    fb_db = auth.firebaseDB()
    user_attribute_dict = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for user_id in user_ids:
            futures.append(
                executor.submit(
                    get_user_attribute, _user_id=user_id, _attribute=attribute
                )
            )

        for future in concurrent.futures.as_completed(futures):
            user_id, status = future.result()
            user_attribute_dict[user_id] = status

    logger.info(f"Got attribute '{attribute}' from firebase for {len(user_ids)} users.")
    return user_attribute_dict


def update_user_data(user_ids: Optional[List[str]] = None) -> None:
    """Copies new users from Firebase to Postgres."""
    # TODO: On Conflict
    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    # get all user_ids from postgres
    query = """SELECT user_id FROM users"""
    postgres_user_info = pg_db.retr_query(query)
    postgres_user_ids = []
    for user_id in postgres_user_info:
        postgres_user_ids.append(user_id[0])
    logger.info(f"There are {len(postgres_user_ids)} users in Postgres.")

    if not user_ids:
        # get all user_ids from firebase
        firebase_user_ids = list(fb_db.reference("v2/users").get(shallow=True).keys())
        logger.info(f"There are {len(firebase_user_ids)} users in Firebase.")
    else:
        firebase_user_ids = user_ids

    # Get difference between firebase users_ids and postgres user_ids.
    # These are new users for which data is only available in Firebase so far.
    new_user_ids = list(set(firebase_user_ids) - set(postgres_user_ids))

    if len(new_user_ids) == 0:
        logger.info("There are NO new users in Firebase.")
    else:
        logger.info(f"There are {len(new_user_ids)} new users in Firebase.")
        # get username and created attributes from firebase
        firebase_usernames_dict = get_user_attribute_from_firebase(
            new_user_ids, "username"
        )
        firebase_created_dict = get_user_attribute_from_firebase(
            new_user_ids, "created"
        )

        # write user information to in memory file
        users_file = io.StringIO("")
        w = csv.writer(users_file, delimiter="\t", quotechar="'")

        for new_user_id in new_user_ids:
            # Get username from dict.
            # Some users might not have a username set in Firebase.
            username = firebase_usernames_dict.get(new_user_id, None)

            # Get created timestamp from dict.
            # Convert timestamp (ISO 8601) from string to a datetime object.
            # Use current timestamp if the value is not set in Firebase
            timestamp = firebase_created_dict.get(new_user_id, None)
            if timestamp:
                created = dt.datetime.strptime(
                    timestamp.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f"
                )
            else:
                # If user has no "created" attribute set it to current time.
                created = dt.datetime.utcnow().isoformat()[0:-3] + "Z"

            w.writerow([new_user_id, username, created])
        users_file.seek(0)

        # write users to users_temp table with copy from statement
        columns = ["user_id", "username", "created"]
        pg_db.copy_from(users_file, "users_temp", columns)
        users_file.close()

        # update username and created attributes in postgres
        query_insert_results = """
            INSERT INTO users
                SELECT * FROM users_temp
            ON CONFLICT (user_id)
            DO NOTHING;
            TRUNCATE users_temp;
        """
        pg_db.query(query_insert_results)
        del pg_db

        logger.info("Updated user data in Postgres.")

    return new_user_ids


def update_user_group_data(user_group_ids: Optional[List[str]] = None) -> List[str]:
    """Copies new user_groups from Firebase to Postgres."""
    pg_db = auth.postgresDB()

    # get all user_group_ids from postgres
    query = """SELECT user_group_id FROM user_groups"""
    postgres_user_group_info = pg_db.retr_query(query)
    postgres_user_group_ids = [
        user_group_id for user_group_id, *_ in postgres_user_group_info
    ]
    logger.info(f"There are {len(postgres_user_group_ids)} user groups in Postgres.")

    if not user_group_ids:
        fb_db = auth.firebaseDB()
        # get all user_group_ids from firebase
        firebase_user_group_ids = list(
            fb_db.reference("v2/userGroups").get(shallow=True).keys()
        )
        logger.info(
            f"There are {len(firebase_user_group_ids)} user groups in Firebase."
        )
    else:
        # FIXME: Make sure user_groups_ids are also in firebase?
        firebase_user_group_ids = user_group_ids

    # Get difference between firebase user_groups_ids and postgres user_group_ids.
    # These are new user_groups for which data is only available in Firebase so far.
    new_user_group_ids = list(
        set(firebase_user_group_ids) - set(postgres_user_group_ids)
    )

    if len(new_user_group_ids) == 0:
        logger.info("There are NO new user groups in Firebase.")
    else:
        logger.info(f"There are {len(new_user_group_ids)} new user groups in Firebase.")

        # write user group information to in memory file
        user_groups_file = io.StringIO("")
        w = csv.writer(user_groups_file, delimiter="\t", quotechar="'")
        w.writerows([[_id] for _id in new_user_group_ids])
        user_groups_file.seek(0)

        # write user_groups to user_groups_temp table with copy from statement
        columns = ["user_group_id"]
        pg_db.copy_from(user_groups_file, "user_groups_temp", columns)
        user_groups_file.close()

        # update username and created attributes in postgres
        query_insert_results = """
            INSERT INTO user_groups
                SELECT * FROM user_groups_temp
            ON CONFLICT (user_group_id)
            DO NOTHING;
            TRUNCATE user_groups_temp;
        """
        pg_db.query(query_insert_results)
        del pg_db

        logger.info("Updated user_group data in Postgres.")

    return new_user_group_ids


def create_update_user_data(user_ids: Optional[List[str]] = None):
    if not user_ids:
        # Nothing to do here.
        return

    fb_db = auth.firebaseDB()

    user_file = io.StringIO("")
    u_w = csv.writer(user_file, delimiter="\t", quotechar="'")
    for _id in user_ids:
        u = fb_db.reference(f"v2/users/{_id}").get()
        if u is None:  # user doesn't exists in FB
            continue
        username = u.get("username")
        updated_at = dt.datetime.utcnow().isoformat()[0:-3] + "Z"
        u_w.writerow([_id, username, updated_at])
    user_file.seek(0)

    pg_db = auth.postgresDB()

    # ---- User Data
    # Clear old temp data
    pg_db.query("TRUNCATE users_temp")
    # Copy user data to temp table
    columns = [
        "user_id",
        "username",
        "updated_at",
    ]
    pg_db.copy_from(user_file, "users_temp", columns)
    user_file.close()

    query_insert_results = """
        INSERT INTO users
            SELECT * FROM users_temp
        ON CONFLICT (user_id) DO UPDATE
        SET
          username = excluded.username,
          updated_at = excluded.updated_at;
        TRUNCATE users_temp;
    """
    pg_db.query(query_insert_results)
    logger.info("Updated user data in Postgres.")
    del pg_db


def update_user_group_full_data(user_group_ids: List[str]):
    fb_db = auth.firebaseDB()

    user_group_file = io.StringIO("")
    user_group_membership_file = io.StringIO("")
    ug_w = csv.writer(user_group_file, delimiter="\t", quotechar="'")
    ugm_w = csv.writer(user_group_membership_file, delimiter="\t", quotechar="'")
    for _id in user_group_ids:
        ug = fb_db.reference(f"v2/userGroups/{_id}").get()
        if ug is None:  # userGroup doesn't exists in FB
            continue
        # New/Updated user group
        created_at = convert_timestamp_to_database_format(ug.get("createdAt"))
        archived_at = convert_timestamp_to_database_format(ug.get("archivedAt"))
        archived_by_id = ug.get("archivedBy", None)
        created_by_id = ug.get("createdBy", None)

        is_archived = archived_by_id is not None

        # NOTE: '\\N' is for null values
        # https://pygresql.readthedocs.io/en/latest/contents/pgdb/cursor.html#pgdb.Cursor.copy_from
        ug_w.writerow(
            [
                _id,
                ug["name"],
                ug.get("description"),
                created_by_id,
                created_at or "\\N",
                archived_by_id,
                archived_at or "\\N",
                is_archived,
            ]
        )
        members = ug.get("users") or {}
        # New/Updated user group memberships
        if members:
            ugm_w.writerows(
                [
                    [
                        _id,  # user-group-id
                        user_id,
                    ]
                    for user_id, is_selected in members.items()
                    if is_selected
                ]
            )
    user_group_file.seek(0)
    user_group_membership_file.seek(0)

    pg_db = auth.postgresDB()

    # ---- User Group Data
    # Clear old temp data
    pg_db.query("TRUNCATE user_groups_temp")
    # Copy user group data to temp table
    columns = [
        "user_group_id",
        "name",
        "description",
        "created_by_id",
        "created_at",
        "archived_by_id",
        "archived_at",
        "is_archived",
    ]
    pg_db.copy_from(user_group_file, "user_groups_temp", columns)
    user_group_file.close()

    # ---- User Group Membership Data
    # Clear old temp data
    pg_db.query("TRUNCATE user_groups_user_memberships_temp")
    # Copy user group membership data to temp table
    columns = ["user_group_id", "user_id"]
    pg_db.copy_from(
        user_group_membership_file,
        "user_groups_user_memberships_temp",
        columns,
    )
    user_group_membership_file.close()

    # Add missing users id.
    query_missing_users = """
        (
            SELECT DISTINCT(ug_temp.user_id)
            FROM user_groups_user_memberships_temp ug_temp
                LEFT JOIN users u USING (user_id)
            WHERE u.user_id is NULL
        )
        UNION
        (
            SELECT DISTINCT(ug_temp.created_by_id)
            FROM user_groups_temp ug_temp
                LEFT JOIN users u ON u.user_id=ug_temp.created_by_id
            WHERE u.user_id is NULL
        )
        UNION
        (
            SELECT DISTINCT(ug_temp.archived_by_id)
            FROM user_groups_temp ug_temp
                LEFT JOIN users u ON u.user_id=ug_temp.archived_by_id
            WHERE u.user_id is NULL
        )
    """

    missing_users_id = [_id for _id, *_ in pg_db.retr_query(query_missing_users)]
    if missing_users_id:
        update_user_data(user_ids=missing_users_id)

    # Remove users which don't exist (For users which are not added by update_user_data)
    delete_memberships_for_non_existing_users = """
        DELETE FROM user_groups_user_memberships_temp WHERE user_id not in (
            SELECT user_id FROM users
        )
    """
    pg_db.query(delete_memberships_for_non_existing_users)
    # Set the created_by and archived_by to
    set_non_existing_created_by = """
        UPDATE user_groups_temp
        SET created_by_id=NULL
        WHERE created_by_id not in (SELECT user_id FROM users)
    """
    pg_db.query(set_non_existing_created_by)
    set_non_existing_archived_by = """
        UPDATE user_groups_temp
        SET archived_by_id=NULL
        WHERE archived_by_id not in (SELECT user_id FROM users)
    """
    pg_db.query(set_non_existing_archived_by)
    # update user_group data from temp table
    query_insert_results = """
        INSERT INTO user_groups
            SELECT * FROM user_groups_temp
        ON CONFLICT (user_group_id) DO UPDATE
        SET
          name = excluded.name,
          description = excluded.description,
          created_at = excluded.created_at,
          archived_at = excluded.archived_at,
          created_by_id = excluded.created_by_id,
          archived_by_id = excluded.archived_by_id,
          is_archived = excluded.is_archived;
        TRUNCATE user_groups_temp;
    """
    pg_db.query(query_insert_results)
    logger.info("Updated user_group data in Postgres.")

    # Update user_group membership data from temp table
    query_insert_results = """
        -- Set all memberships as inactive for selected user-group-ids
        UPDATE user_groups_user_memberships
        SET is_active = FALSE
        WHERE user_group_id = ANY(%s);
        -- Add/Set active for active memberships
        INSERT INTO user_groups_user_memberships
            SELECT *, TRUE FROM user_groups_user_memberships_temp
        ON CONFLICT (user_group_id, user_id) DO UPDATE
            SET is_active = excluded.is_active;
        -- Clear temp table data
        TRUNCATE user_groups_user_memberships_temp;
    """
    pg_db.query(query_insert_results, [user_group_ids])
    logger.info("Updated user_group membership data in Postgres.")

    del pg_db


def create_update_membership_data(
    membership_ids: Optional[List[str]] = None,
):
    if not membership_ids:
        # Nothing to do here
        return

    fb_db = auth.firebaseDB()

    membership_file = io.StringIO("")
    m_w = csv.writer(membership_file, delimiter="\t", quotechar="'")
    for _id in membership_ids:
        u = fb_db.reference(f"v2/userGroupMembershipLogs/{_id}").get()
        if u is None:  # user doesn't exists in FB
            continue
        user_group_id = u.get("userGroupId")
        user_id = u.get("userId")
        action = u.get("action")
        timestamp = convert_timestamp_to_database_format(u.get("timestamp"))
        m_w.writerow(
            [
                _id,
                user_group_id,
                user_id,
                action,
                timestamp,
            ]
        )
    membership_file.seek(0)

    pg_db = auth.postgresDB()

    # Clear old memberships logs
    pg_db.query("TRUNCATE user_groups_membership_logs_temp")
    # Copy user group membership log data to temp table
    columns = [
        "membership_id",
        "user_group_id",
        "user_id",
        "action",
        "timestamp",
    ]
    pg_db.copy_from(
        membership_file,
        "user_groups_membership_logs_temp",
        columns,
    )
    membership_file.close()
    query_insert_results = """
        INSERT INTO user_groups_membership_logs
            SELECT * FROM user_groups_membership_logs_temp
        WHERE membership_id = ANY(%s);
        -- Clear temp table data
        TRUNCATE user_groups_membership_logs_temp;
    """
    pg_db.query(query_insert_results, [membership_ids])
    logger.info("Updated user_group membership logs data in Postgres.")
    del pg_db


def get_project_attribute_from_firebase(project_ids: List[str], attribute: str):
    """Use threading to query a project attribute in firebase.

    Follows a workflow describted in this blogpost:
    https://www.digitalocean.com/community/tutorials/how-to-use-threadpoolexecutor-in-python-3
    """

    def get_project_attribute(_project_id, _attribute):
        try:
            ref = fb_db.reference(f"v2/projects/{_project_id}/{_attribute}")
        except TransportError as e:
            logger.exception(e)
            logger.info(
                "Failed to estabilish a connection to Firebase. Retry will be attempted upon the next function call."
            )
            attribute_value = None
        return [_project_id, ref.get()]

    fb_db = auth.firebaseDB()
    project_attribute_dict = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for project_id in project_ids:
            futures.append(
                executor.submit(
                    get_project_attribute, _project_id=project_id, _attribute=attribute
                )
            )

        for future in concurrent.futures.as_completed(futures):
            project_id, status = future.result()
            project_attribute_dict[project_id] = status

    logger.info(
        f"Got attribute '{attribute}' from firebase for {len(project_ids)} projects."
    )
    return project_attribute_dict


def update_project_data(project_ids: list = []):
    """Get status of projects from Firebase and updates them in Postgres.

    Default behavior is to check all projects, which have not been archived
    and update projects in postgres for which the status has changed.
    If called with a list of project ids as parameter
    only those projects will be updated.
    """

    pg_db = auth.postgresDB()

    if project_ids:
        # use project ids passed by user
        query = """
            select project_id, status from projects
            where project_id IN %s;
        """
        project_info = pg_db.retr_query(query, [tuple(project_ids)])
        logger.info("got projects from postgres based on user input")
    else:
        # get project ids for all non-archived projects in postgres
        query = """
            select project_id, status from projects
            where status != 'archived';
        """
        project_info = pg_db.retr_query(query)
        project_ids = []
        for project_id, attribute in project_info:
            project_ids.append(project_id)
        logger.info(
            f"Got all ({len(project_ids)}) not-archived projects from postgres."
        )

    # get project status from firebase
    if len(project_ids) > 0:
        project_status_dict = get_project_attribute_from_firebase(project_ids, "status")

        for project_id, postgres_status in project_info:
            # for each project we check if the status set in firebase
            # and the status set in postgres are different
            # we update status in postgres if value has changed
            firebase_status = project_status_dict[project_id]
            if postgres_status == firebase_status or firebase_status is None:
                # project status did not change or
                # project status is not available in firebase
                pass
            else:
                # The status of the project has changed.
                # The project status will be updated in postgres.
                # Project status will only change for few (<10) projects at once.
                # Using multiple update operations seems to be okay in this scenario.
                query_update_project = """
                    UPDATE projects
                    SET status=%s
                    WHERE project_id=%s;
                """
                data_update_project = [firebase_status, project_id]
                pg_db.query(query_update_project, data_update_project)
                logger.info(
                    f"Updated project status in Postgres for project {project_id}"
                )

    logger.info("Finished status update projects.")


def get_project_progress(project_id: str) -> int:
    """
    Calculate overall project progress as the average progress for all groups.
    This is not hundred percent exact, since groups can have a different number of tasks
    but it is still "good enough" and gives almost correct progress.
    But it is easier to compute than considering the actual number of tasks per group.

    NOTE: the cast to integer in postgres rounds decimals. This means that for 99.5%
    progress, we return 100% here. We should evaluate if this is what we want if/when
    we introduce automated project rotation upon completion (as the reported completion
    would happen 0.5% before actual completion).
    """
    pg_db = auth.postgresDB()
    query = """
        select
          avg(group_progress)::integer as progress
        from
        (
            -- Get all groups for this project and
            -- add progress for groups that have been worked on already.
            -- Set progress to 0 if no user has worked on this group.
            -- For groups that no users worked on
            -- there are no entries in the results table.
            select
              g.group_id
              ,g.project_id
              ,case
                when group_progress is null then 0
                else group_progress
              end as group_progress
            from groups g
            left join
                (
                -- Here we get the progress for all groups
                -- for which results have been submitted already.
                -- Progress for a group can be max 100
                -- even if more users than required submitted results.
                -- The verification number of a project is used here.
                select
                  ms.group_id
                  ,ms.project_id
                  ,case
                    when count(distinct user_id) >= p.verification_number then 100
                    else 100 * count(distinct user_id) / p.verification_number
                  end as group_progress
                from mapping_sessions ms, projects p
                where ms.project_id = p.project_id
                group by group_id, ms.project_id, p.verification_number
            ) bar
            on bar.group_id = g.group_id and bar.project_id = g.project_id
            where g.project_id = %s
        ) foo
        group by project_id
    """
    data = [project_id]
    return pg_db.retr_query(query, data)[0][0]


def set_progress_in_firebase(project_id: str):
    """Update the project progress value in Firebase."""
    progress = get_project_progress(project_id)

    fb_db = auth.firebaseDB()
    project_progress_ref = fb_db.reference(f"v2/projects/{project_id}/progress")
    project_progress_ref.set(progress)
    logger.info(f"set progress for project {project_id}: {progress}")


def get_contributor_count_from_postgres(project_id: str) -> int:
    pg_db = auth.postgresDB()
    query = """
        select
          count(distinct user_id)
        from mapping_sessions ms
        where
          project_id = %s
    """
    data = [project_id]
    return pg_db.retr_query(query, data)[0][0]


def set_contributor_count_in_firebase(project_id: str):
    """Update the project contributors value in Firebase."""

    contributor_count = get_contributor_count_from_postgres(project_id)
    fb_db = auth.firebaseDB()
    project_progress_ref = fb_db.reference(f"v2/projects/{project_id}/contributorCount")
    project_progress_ref.set(contributor_count)
    logger.info(
        f"set contributorCount attribute for project {project_id}: {contributor_count}"
    )


def set_tileserver_api_key(project_id: str, api_key: str) -> None:
    """Set the tileserver api key value in Firebase."""

    fb_db = auth.firebaseDB()
    project_progress_ref = fb_db.reference(
        f"v2/projects/{project_id}/tileServer/apiKey"
    )
    project_progress_ref.set(api_key)
    logger.info(f"set tileServer/apiKey attribute for project: {project_id}")
