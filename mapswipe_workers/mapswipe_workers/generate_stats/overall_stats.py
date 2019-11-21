import os
import pandas as pd
from mapswipe_workers import auth
from mapswipe_workers.definitions import logger
from mapswipe_workers.utils import geojson_functions


def get_overall_stats(filename: str) -> pd.DataFrame:
    """
    The function queries the projects table and row_counts table in postgres.
    The query results are stored in the specified csv file.
    And also returned as a pandas DataFrame.

    Parameters
    ----------
    filename: str
    """

    pg_db = auth.postgresDB()
    sql_query = """
            COPY (
                SELECT
                  'all' as status
                  ,count(*) as count_projects
                  ,round(SUM(ST_Area(geom::geography)/(1000*1000))::numeric, 1) as area_projects_sqkm
                  ,(SELECT reltuples FROM row_counts WHERE relname = 'groups') as count_groups
                  ,(SELECT reltuples FROM row_counts WHERE relname = 'tasks') as count_tasks
                  ,(SELECT reltuples FROM row_counts WHERE relname = 'results') as count_results
                  ,(SELECT count(*) FROM users) as count_users
                  ,clock_timestamp()
                FROM projects
                UNION
                SELECT
                  status
                  ,count(*) as count_projects
                  ,round(SUM(ST_Area(geom::geography)/(1000*1000))::numeric, 1) as area_sqkm
                  ,NULL
                  ,NULL
                  ,NULL
                  ,NULL
                  ,clock_timestamp()
                FROM projects
                GROUP BY
                  status
                ORDER BY count_tasks
            ) TO STDOUT WITH CSV HEADER"""

    with open(filename, "w") as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db
    logger.info("got overall stats from postgres.")

    df = pd.read_csv(filename)
    return df


def get_project_static_info(filename: str) -> pd.DataFrame:
    """
    The function queries the projects table.
    Each row represents a single project and provides the information which is static.
    By static we understand all attributes which are not affected by new results being contributed.
    The results are stored in a csv file and also returned as a pandas DataFrame.

    Parameters
    ----------
    filename: str
    """

    pg_db = auth.postgresDB()
    sql_query = """
        COPY (
            SELECT 
                project_id
                ,name
                ,project_details
                ,look_for
                ,project_type
                ,status
                ,ST_Area(geom::geography)/1000000 as area_sqkm
                ,ST_AsText(geom) as geom
                ,ST_AsText(ST_Centroid(geom)) as centroid
            FROM projects
        ) TO STDOUT WITH CSV HEADER"""

    with open(filename, "w") as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db
    logger.info("got projects from postgres.")

    df = pd.read_csv(filename)
    return df


def load_project_info_dynamic(filename: str) -> pd.DataFrame:
    """
    The function loads data from a csv file into a pandas dataframe.
    If not file exists, it will be initialized.

    Parameters
    ----------
    filename: str
    """

    if os.path.isfile(filename):
        logger.info(f"file {filename} exists. Init from this file.")
        df = pd.read_csv(filename, index_col="idx")
    else:
        columns = [
            "project_id",
            "progress",
            "number_of_users",
            "number_of_results",
            "number_of_results_progress",
            "day",
        ]
        df = pd.DataFrame(index=[], columns=columns)
        df["project_id"].astype("str")

    return df


def save_projects(filename: str, df: pd.DataFrame, df_dynamic: pd.DataFrame) -> None:
    """
    The function merges the dataframes for static and dynamic project information
    and then save the result as csv file.
    Additionally, two geojson files are generated using
    (a) the geometry of the projects and
    (b) the centroid of the projects.

    Parameters
    ----------
    filename: str
    df: pd.DataFrame
    df_dynamic: pd.DataFrame
    """

    projects_df = df.merge(
        df_dynamic, left_on="project_id", right_on="project_id", how="left"
    )
    projects_df.to_csv(filename, index_label="idx")
    logger.info(f"saved projects: {filename}")
    geojson_functions.csv_to_geojson(filename, "geom")
    geojson_functions.csv_to_geojson(filename, "centroid")
