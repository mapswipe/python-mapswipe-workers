from mapswipe_workers.definitions import logger
from mapswipe_workers.definitions import DATA_PATH

from mapswipe_workers.generate_stats import project_stats
from mapswipe_workers.generate_stats import overall_stats


def generate_stats(project_id_list, all_projects=False):

    projects_info_filename = f'{DATA_PATH}/api-data/projects/projects_static.csv'
    projects_df = overall_stats.get_project_static_info(projects_info_filename)

    projects_info_dynamic_filename = f'{DATA_PATH}/api-data/projects/projects_dynamic.csv'
    projects_dynamic_df = overall_stats.load_project_info_dynamic(projects_info_dynamic_filename)

    if all_projects:
        project_id_list = projects_df['project_id'].to_list()
        logger.info(f'will generate stats for all projects.')

    logger.info(f'will generate stats for: {project_id_list}')

    # get per project stats and aggregate based on task_id
    for project_id in project_id_list:

        # check if project id is correct
        if not project_id in projects_df['project_id'].to_list():
            logger.info(f'project {project_id} does not exist. skip this one.')
            continue

        logger.info(f'start generate stats for project: {project_id}')
        idx = projects_dynamic_df.index[projects_dynamic_df['project_id'] == project_id].tolist()
        if len(idx) > 0:
            projects_dynamic_df.drop([idx[0]], inplace=True)

        # aggregate results and get per project statistics
        project_stats_dict = project_stats.get_per_project_statistics(project_id)
        if project_stats_dict:
            projects_dynamic_df = projects_dynamic_df.append(project_stats_dict, ignore_index=True)
            projects_dynamic_df.to_csv(projects_info_dynamic_filename, index_label='idx')

            # TODO: for build area projects generate tasking manager geometries

    # merge static info and dynamic info and save
    if len(project_id_list) > 0:
        projects_filename = f'{DATA_PATH}/api-data/projects/projects.csv'
        overall_stats.save_projects(projects_filename, projects_df, projects_dynamic_df)