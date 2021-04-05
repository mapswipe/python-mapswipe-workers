"""Update users and project information from Firebase in Postgres."""

import asyncio
import concurrent.futures
import csv
import datetime as dt
import io
from typing import List, Optional

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def get_user_attribute_from_firebase(user_ids: List[str], attribute: str):
    """Use async for firebase sdk to query a user attribute.

    Follows a workflow describted in this blogpost:
    https://hiranya911.medium.com/firebase-python-admin-sdk-with-asyncio-d65f39463916
    """

    async def get_user_attribute(user_id, event_loop):
        ref = fb_db.reference(f"v2/users/{user_id}/{attribute}")
        # Blocking method is delegated to the thread pool
        return [user_id, await event_loop.run_in_executor(executor, ref.get)]

    async def get_user_attribute_list(user_ids, event_loop):
        coroutines = [get_user_attribute(i, event_loop) for i in user_ids]
        completed, pending = await asyncio.wait(coroutines)
        firebase_attribute_dict = {}
        for item in completed:
            user_id, attribute_value = item.result()
            firebase_attribute_dict[user_id] = attribute_value
        return firebase_attribute_dict

    fb_db = auth.firebaseDB()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    event_loop = asyncio.new_event_loop()
    try:
        user_attribute_dict = event_loop.run_until_complete(
            get_user_attribute_list(user_ids, event_loop)
        )
    finally:
        event_loop.close()

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
    logger.info(f"There {len(postgres_user_ids)} users in Postgres.")

    if not user_ids:
        # get all user_ids from firebase
        firebase_user_ids = list(fb_db.reference("v2/users").get(shallow=True).keys())
        logger.info(f"There {len(firebase_user_ids)} users in Firebase.")
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

        for i, new_user in enumerate(new_user_ids):
            # Get username from dict.
            # Some users might not have a username set in Firebase.
            username = firebase_usernames_dict.get(new_user, None)

            # Get created timestamp from dict.
            # Convert timestamp (ISO 8601) from string to a datetime object.
            # Use current timestamp if the value is not set in Firebase
            timestamp = firebase_created_dict.get(user_id, None)
            if timestamp:
                created = dt.datetime.strptime(
                    timestamp.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f"
                )
            else:
                # If user has no "created" attribute set it to current time.
                created = dt.datetime.utcnow().isoformat()[0:-3] + "Z"

            w.writerow([new_user, username, created])
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


def get_project_attribute_from_firebase(project_ids: List[str], attribute: str):
    """Use async for firebase sdk to query a project attribute.

    Follows a workflow describted in this blogpost:
    https://hiranya911.medium.com/firebase-python-admin-sdk-with-asyncio-d65f39463916
    """

    async def get_project_status(project_id, event_loop):
        ref = fb_db.reference(f"v2/projects/{project_id}/{attribute}")
        # Blocking method is delegated to the thread pool
        return [project_id, await event_loop.run_in_executor(executor, ref.get)]

    async def get_project_status_list(project_ids, event_loop):
        coroutines = [get_project_status(i, event_loop) for i in project_ids]
        completed, pending = await asyncio.wait(coroutines)
        firebase_attribute_dict = {}
        for item in completed:
            project_id, attribute_value = item.result()
            firebase_attribute_dict[project_id] = attribute_value
        return firebase_attribute_dict

    fb_db = auth.firebaseDB()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    event_loop = asyncio.new_event_loop()
    try:
        project_attribute_dict = event_loop.run_until_complete(
            get_project_status_list(project_ids, event_loop)
        )
    finally:
        event_loop.close()

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
    project_status_dict = get_project_attribute_from_firebase(project_ids, "status")

    for i, project in enumerate(project_info):
        # for each project we check if the status set in firebase
        # and the status set in postgres are different
        # we update status in postgres if value has changed
        project_id, postgres_status = project
        firebase_status = project_status_dict[project_id]
        if postgres_status == firebase_status or firebase_status is None:
            # project status did not change or
            # project status is not available in firebase
            pass
        else:
            # The status of the project has changed.
            # The project status will be updated in postgres.
            # Usually, project status will only change for few (<10) projects at once.
            # Using multiple update operations seems to be okay in this scenario.
            query_update_project = """
                UPDATE projects
                SET status=%s
                WHERE project_id=%s;
            """
            data_update_project = [firebase_status, project_id]
            pg_db.query(query_update_project, data_update_project)
            logger.info(f"Updated project status in Postgres for project {project_id}")

    logger.info("Finished status update projects.")


def set_progress_in_firebase(project_id: str):
    """Update the project progress value in Firebase."""

    pg_db = auth.postgresDB()
    query = """
        -- Calculate overall project progress as
        -- the average progress for all groups.
        -- This is not hundred percent exact,
        -- since groups can have a different number of tasks
        -- but it is still "good enough" and gives almost correct progress.
        -- But it is easier to compute
        -- than considering the actual number of tasks per group.
        select
          project_id
          ,avg(group_progress)::integer as progress
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
                  r.group_id
                  ,r.project_id
                  ,case
                    when count(distinct user_id) >= p.verification_number then 100
                    else 100 * count(distinct user_id) / p.verification_number
                  end as group_progress
                from results r, projects p
                where r.project_id = p.project_id
                group by group_id, r.project_id, p.verification_number
            ) bar
            on bar.group_id = g.group_id and bar.project_id = g.project_id
            where g.project_id = %s
        ) foo
        group by project_id
    """
    data = [project_id]
    progress = pg_db.retr_query(query, data)[0][1]

    fb_db = auth.firebaseDB()
    project_progress_ref = fb_db.reference(f"v2/projects/{project_id}/progress")
    project_progress_ref.set(progress)
    logger.info(f"set progress for project {project_id}: {progress}")


def set_contributor_count_in_firebase(project_id: str):
    """Update the project contributors value in Firebase."""

    pg_db = auth.postgresDB()
    query = """
        select
          project_id
          ,count(distinct user_id) contributor_count
        from results r
        where
          project_id = %s
        group by project_id
    """
    data = [project_id]
    contributor_count = pg_db.retr_query(query, data)[0][1]

    fb_db = auth.firebaseDB()
    project_progress_ref = fb_db.reference(f"v2/projects/{project_id}/contributorCount")
    project_progress_ref.set(contributor_count)
    logger.info(
        f"set contributorCount attribute for project {project_id}: {contributor_count}"
    )
