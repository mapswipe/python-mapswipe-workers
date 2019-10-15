from psycopg2 import sql
from mapswipe_workers import auth
from mapswipe_workers.definitions import logger

def get_results_by_task_id(filename, project_id):
    '''
    Export aggregated results on a task_id basis per project.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        """
        DROP TABLE IF EXISTS agg_results;
        CREATE TEMP TABLE agg_results AS
        select
            project_id
            ,group_id
            ,task_id
            ,count(*) as total_results_count
            ,sum(CASE WHEN result = 0 THEN 1 ELSE 0	END) AS "0_results_count"
            ,sum(CASE WHEN result = 1 THEN 1 ELSE 0	END) AS "1_results_count"
            ,sum(CASE WHEN result = 2 THEN 1 ELSE 0	END) AS "2_results_count"
            ,sum(CASE WHEN result = 3 THEN 1 ELSE 0	END) AS "3_results_count"
            ,round(sum(CASE WHEN result = 0 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "0_results_share"
            ,round(sum(CASE WHEN result = 1 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "1_results_share"
            ,round(sum(CASE WHEN result = 2 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "2_results_share"
            ,round(sum(CASE WHEN result = 3 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "3_results_share"
            ,min(timestamp) as first_timestamp
            ,max(timestamp) as last_timestamp
        from
            results
        where
            project_id = {}
        group by
            project_id, group_id, task_id;

        DROP TABLE IF EXISTS agg_results_with_agreement;
        CREATE TEMP TABLE agg_results_with_agreement AS
        SELECT
          a.*
          ,CASE WHEN total_results_count = 1 THEN 1.0	ELSE (
              round(
                  ((1.0 / (total_results_count::numeric * (total_results_count::numeric - 1.0)))
                  *
                  (
                  (("0_results_count"::numeric ^ 2.0) - "0_results_count"::numeric)
                  +
                  (("1_results_count"::numeric ^ 2.0) - "1_results_count"::numeric)
                  +
                  (("2_results_count"::numeric ^ 2.0) - "2_results_count"::numeric)
                  +
                  (("3_results_count"::numeric ^ 2.0) - "3_results_count"::numeric)
                  ))
              ,3)
            ) END as agreement
        FROM
          agg_results as a;

        DROP TABLE IF EXISTS project_tasks;
        CREATE TEMP TABLE project_tasks AS
        SELECT
          t.task_id
          ,t.group_id
          ,t.project_id
          ,ST_AsText(t.geom) as geom
        FROM
          tasks as t
        WHERE
          t.project_id = {};

        COPY
        (
            SELECT
              t.task_id
              ,t.group_id
              ,t.project_id
              ,t.geom
              ,a.total_results_count
              ,a."0_results_count"
              ,a."1_results_count"
              ,a."2_results_count"
              ,a."3_results_count"
              ,a."0_results_share"
              ,a."1_results_share"
              ,a."2_results_share"
              ,a."3_results_share"
              ,a.agreement
            FROM
              project_tasks as t
            LEFT JOIN
              agg_results_with_agreement as a
            ON
              t.task_id = a.task_id
              AND
              t.group_id = a.group_id
              AND
              t.project_id = a.project_id
        )  TO STDOUT WITH CSV HEADER

        """).format(sql.Literal(project_id), sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by task_id for project %s to %s' % (project_id, filename))


def get_progress_by_date(filename, project_id):
    '''
    Export aggregated progress on a project_id and daily basis as csv file.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
    """
    DROP TABLE IF EXISTS v2_res_by_project_group_day;
    CREATE TEMP TABLE v2_res_by_project_group_day AS
    SELECT
      r.project_id
      ,r.group_id
      ,Min(g.number_of_tasks) as number_of_tasks
      ,Min(g.required_count + g.finished_count) as number_of_users_required
      -- the following attributes are dynamic
      -- could also set to hour if needed, of make this a as a parameter
      ,date_trunc('day', timestamp) as day
      ,count(distinct(user_id)) as number_of_users
      ,count(distinct(user_id)) * Min(g.number_of_tasks) as number_of_results
    FROM
      results as r, groups as g
    WHERE
      r.project_id = g.project_id
      AND
      r.group_id = g.group_id
      AND
      -- use a single project id or a list of projects
      r.project_id = {}
    GROUP BY
      r.project_id
      ,r.group_id
      ,day;

    DROP TABLE IF EXISTS v2_progress_by_project_group_day;
    CREATE TEMP TABLE v2_progress_by_project_group_day AS
    SELECT
      project_id
      ,group_id
      ,number_of_tasks
      ,number_of_users_required
      ,day
      ,number_of_users
      ,number_of_results
      ,SUM(number_of_users) OVER (PARTITION BY project_id, group_id ORDER BY day) as cum_number_of_users
      ,SUM(number_of_results) OVER (PARTITION BY project_id, group_id ORDER BY day) as cum_number_of_results
    FROM
      v2_res_by_project_group_day
    ORDER BY
      project_id, group_id, day;

    DROP TABLE IF EXISTS v2_correct_by_project_group_day;
    CREATE TEMP TABLE v2_correct_by_project_group_day AS
    SELECT
      r.*
      ,CASE
        WHEN cum_number_of_users <= number_of_users_required THEN cum_number_of_users
        ELSE number_of_users_required
      END as cum_number_of_users_progress
      ,CASE
        WHEN cum_number_of_users <= number_of_users_required THEN cum_number_of_results
        ELSE cum_number_of_results - ((cum_number_of_users - number_of_users_required) * number_of_tasks)
      END as cum_number_of_results_progress
      ,CASE
        WHEN cum_number_of_users <= number_of_users_required THEN number_of_results
        WHEN (cum_number_of_users - number_of_users) < number_of_users_required THEN (number_of_users_required - (cum_number_of_users - number_of_users)) * number_of_tasks
        ELSE 0
      END as number_of_results_progress
    FROM
      v2_progress_by_project_group_day as r;

    COPY
    (
        SELECT
          r.project_id
          ,r.day
          ,SUM(r.number_of_results) as number_of_results
          ,SUM(r.number_of_results_progress) as number_of_results_progress
          ,SUM(SUM(r.number_of_results)) OVER (PARTITION BY r.project_id ORDER BY day) as cum_number_of_results
          ,SUM(SUM(r.number_of_results_progress)) OVER (PARTITION BY r.project_id ORDER BY day) as cum_number_of_results_progress
          ,Min(p.required_results) as required_results
          ,Round(SUM(SUM(r.number_of_results_progress)) OVER (PARTITION BY r.project_id ORDER BY day) / Min(p.required_results), 3) as progress
        FROM
          v2_correct_by_project_group_day as r
          ,projects as p
        WHERE
          p.project_id = r.project_id
        GROUP BY
          r.project_id
          ,r.day
        ORDER BY
          r.project_id,
          r.day
    ) TO STDOUT WITH CSV HEADER
    """).format(sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated progress by project_id and date for project %s to %s' % (project_id, filename))


def get_contributors_by_date(filename, project_id):
    '''
    Export aggregated progress on a project_id and daily basis as csv file.

    Parameters
    ----------
    filename: str
    project_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
    """
    ---
    """).format(sql.Literal(project_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated progress by project_id and date for project %s to %s' % (project_id, filename))

