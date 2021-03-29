"""Update users and project information from Firebase in Postgres."""

import datetime as dt
import asyncio
import concurrent.futures
from typing import List

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger, sentry


def get_last_updated_timestamp() -> str:
    """Get the timestamp of the latest created user in Postgres."""
    pg_db = auth.postgresDB()
    query = """
        SELECT created
        FROM users
        WHERE created IS NOT NULL
        ORDER BY created DESC
        LIMIT 1
        """
    last_updated = pg_db.retr_query(query)
    try:
        last_updated = last_updated[0][0]
        last_updated = last_updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        logger.info("Last updated users: {0}".format(last_updated))
    except (IndexError, AttributeError):
        logger.exception("Could not get last timestamp of users.")
        sentry.capture_exception()
        last_updated = ""
    return last_updated


def update_user_data(user_ids: list = []) -> None:
    """Copies new users from Firebase to Postgres."""
    # TODO: On Conflict
    fb_db = auth.firebaseDB()
    pg_db = auth.postgresDB()

    ref = fb_db.reference("v2/users")
    last_updated = get_last_updated_timestamp()

    if user_ids:
        logger.info("Add custom user ids to user list, which will be updated.")
        users = {}
        for user_id in user_ids:
            users[user_id] = ref.child(user_id).get()
    elif last_updated:
        # Get only new users from Firebase.
        query = ref.order_by_child("created").start_at(last_updated)
        users = query.get()
        if len(users) == 0:
            logger.info("there are no new users in Firebase.")
        else:
            # Delete first user in ordered dict (FIFO).
            # This user is already in the database (user.created = last_updated).
            users.popitem(last=False)
    else:
        # Get all users from Firebase.
        users = ref.get()

    for user_id, user in users.items():
        # Convert timestamp (ISO 8601) from string to a datetime object.
        try:
            created = dt.datetime.strptime(
                user["created"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f"
            )
        except KeyError:
            # If user has no "created" attribute set it to current time.
            created = dt.datetime.utcnow().isoformat()[0:-3] + "Z"
            logger.info(
                "user {0} didn't have a 'created' attribute. ".format(user_id)
                + "Set it to '{0}' now.".format(created)
            )
        username = user.get("username", None)
        query_update_user = """
            INSERT INTO users (user_id, username, created)
            VALUES(%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET username=%s,
            created=%s;
        """
        data_update_user = [
            user_id,
            username,
            created,
            username,
            created,
        ]
        pg_db.query(query_update_user, data_update_user)
    logger.info("Updated user data in Potgres.")


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
        firebase_status_dict = {}
        for item in completed:
            project_id, firebase_status = item.result()
            firebase_status_dict[project_id] = firebase_status
        return firebase_status_dict

    fb_db = auth.firebaseDB()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    event_loop = asyncio.new_event_loop()
    try:
        project_attribute_dict = event_loop.run_until_complete(get_project_status_list(project_ids, event_loop))
    finally:
        event_loop.close()

    logger.info(f"Got project attribute '{attribute}' from firebase for {len(project_ids)} projects.")
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
        logger.info(f"Got all ({len(project_ids)}) not-archived projects from postgres.")

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
        -- This is not hundred percent exact, since groups can have a different number of tasks
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
    logger.info(f"set contributorCount attribute for project {project_id}: {contributor_count}")
