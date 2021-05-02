from mapswipe_workers import auth
from mapswipe_workers.definitions import logger, sentry


def get_project_ids_from_postgres():
    """Get project ids."""

    p_con = auth.postgresDB()

    query = """
        SELECT project_id FROM projects;
    """
    data = p_con.retr_query(query)
    project_ids = [item[0] for item in data]

    logger.info("Got projects from postgres.")
    logger.info(project_ids)
    return project_ids


def update_tasks_table(project_id: str):
    """Remove duplicates in 'project_types_specifics' attribute in tasks table."""

    logger.info(f"Start process for project: '{project_id}'")
    p_con = auth.postgresDB()

    query = """
            UPDATE tasks
            SET project_type_specifics = project_type_specifics::jsonb
                #- '{projectId}'
                #- '{groupId}'
                #- '{taskId}'
                #- '{geometry}'
                #- '{wkt}'
            WHERE project_id = %(project_id)s
        """
    try:
        p_con.query(query, {"project_id": project_id})
        logger.info(f"Updated tasks table for project '{project_id}'.")
    except Exception as e:
        sentry.capture_exception(e)
        sentry.capture_message(
            f"Could NOT update tasks table for project '{project_id}'."
        )
        logger.exception(e)
        logger.warning(f"Could NOT update tasks table for project '{project_id}'.")


def update_groups_table(project_id: str):
    """Remove duplicates in 'project_types_specifics' attribute in groups table."""

    logger.info(f"Start process for project: '{project_id}'")
    p_con = auth.postgresDB()

    query = """
        UPDATE groups
        SET project_type_specifics = project_type_specifics::jsonb
            #- '{projectId}'
            #- '{id}'
            #- '{requiredCount}'
            #- '{finishedCount}'
            #- '{neededCount}'
            #- '{reportCount}'
            #- '{distributedCount}'
        WHERE project_id = %(project_id)s
    """
    try:
        p_con.query(query, {"project_id": project_id})
        logger.info(f"Updated tasks table for project '{project_id}'.")
    except Exception as e:
        sentry.capture_exception(e)
        sentry.capture_message(
            f"Could NOT update tasks table for project '{project_id}'."
        )
        logger.exception(e)
        logger.warning(f"Could NOT update tasks table for project '{project_id}'.")


def run_vacuum_tasks_table():
    """Run vacuum to reclaim storage."""
    logger.info("Start vacuum on tasks table.")
    p_con = auth.postgresDB()
    # isolation_level 0 will move you out of a transaction block
    old_isolation_level = p_con._db_connection.isolation_level
    p_con._db_connection.set_isolation_level(0)
    query = """
            VACUUM FULL tasks
        """
    p_con.query(query)
    # set isolation_level back to initial value
    p_con._db_connection.set_isolation_level(old_isolation_level)
    logger.info("Finish vacuum on tasks table.")


def run_vacuum_groups_table():
    """Run vacuum to reclaim storage."""
    logger.info("Start vacuum on groups table.")
    p_con = auth.postgresDB()
    # isolation_level 0 will move you out of a transaction block
    old_isolation_level = p_con._db_connection.isolation_level
    p_con._db_connection.set_isolation_level(0)
    query = """
            VACUUM FULL groups
        """
    p_con.query(query)
    # set isolation_level back to initial value
    p_con._db_connection.set_isolation_level(old_isolation_level)
    logger.info("Finish vacuum on groups table.")


if __name__ == "__main__":
    project_ids_list = get_project_ids_from_postgres()
    for i, project_id in enumerate(project_ids_list):
        update_tasks_table(project_id)
        update_groups_table(project_id)
        # vacuum every 50th project
        if i % 50 == 0 or i == len(project_ids_list) - 1:
            run_vacuum_tasks_table()
            run_vacuum_groups_table()
