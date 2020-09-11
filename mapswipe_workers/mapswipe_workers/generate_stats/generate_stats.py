from mapswipe_workers.definitions import logger
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.generate_stats import project_stats, overall_stats


def generate_stats(project_id_list: list):
    """
    Query attributes for all projects from postgres projects table
    Write information on status (e.g. active, inactive, finished) and further
    attributes for all projects to projects_static.csv.
    Computationally more expensive tasks are only performed for projects
    specified in project_id_list.
    Write information on progress and contributors and further attributes
    only for projects specified in project_id_list to projects_dynamic.csv.
    Write information on project progress history and aggregated results
    only for projects specified in project_id_list to csv and geojson files.
    Merge projects_static.csv and projects_dynamic.csv into projects.csv.
    Convert projects.csv file into GeoJSON format using project geometry
    and project centroid.

    Parameters
    ----------
    project_id_list: list
    """

    logger.info(f"will generate stats for: {project_id_list}")
    projects_info_filename = f"{DATA_PATH}/api/projects/projects_static.csv"
    projects_df = overall_stats.get_project_static_info(projects_info_filename)
    project_id_list_postgres = projects_df["project_id"].to_list()

    projects_info_dynamic_filename =\
        f"{DATA_PATH}/api/projects/projects_dynamic.csv"
    projects_dynamic_df = overall_stats.load_project_info_dynamic(
        projects_info_dynamic_filename
    )

    # get per project stats and aggregate based on task_id
    for project_id in project_id_list:

        # check if project id is existing
        if project_id not in project_id_list_postgres:
            logger.info(f"project {project_id} does not exist. skip this one.")
            continue

        project_info = projects_df.loc[projects_df["project_id"] == project_id]

        logger.info(f"start generate stats for project: {project_id}")
        idx = projects_dynamic_df.index[
            projects_dynamic_df["project_id"] == project_id
        ].tolist()
        if len(idx) > 0:
            projects_dynamic_df.drop([idx[0]], inplace=True)

        # aggregate results and get per project statistics
        project_stats_dict = project_stats.get_per_project_statistics(
            project_id, project_info
        )
        if project_stats_dict:
            projects_dynamic_df = projects_dynamic_df.append(
                project_stats_dict, ignore_index=True
            )
            projects_dynamic_df.to_csv(
                projects_info_dynamic_filename, index_label="idx"
            )

    if len(project_id_list) > 0:
        # merge static info and dynamic info and save
        projects_filename = f"{DATA_PATH}/api/projects/projects.csv"
        projects_df = overall_stats.save_projects(
            projects_filename, projects_df, projects_dynamic_df
        )

        # generate overall stats for active, inactive, finished projects
        overall_stats_filename = f"{DATA_PATH}/api/stats.csv"
        overall_stats.get_overall_stats(projects_df, overall_stats_filename)

    logger.info(f"finished generate stats for: {project_id_list}")


def generate_stats_all_projects():
    """
    queries all existing project ids from postgres projects table
    saves them into a csv file and returns a list of all project ids
    then generates project statistics using the derived list of project ids
    """

    logger.info("will generate stats for all projects.")

    # get all project ids from postgres database
    projects_info_filename = f"{DATA_PATH}/api/projects/projects_static.csv"
    projects_df = overall_stats.get_project_static_info(projects_info_filename)
    project_id_list = projects_df["project_id"].to_list()

    # generate stats for the derived project ids
    generate_stats(project_id_list)
