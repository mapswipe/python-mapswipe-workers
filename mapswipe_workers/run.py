import json
import os
import time

import click
import schedule

from mapswipe_workers import auth
from mapswipe_workers import generate_stats
from mapswipe_workers import transfer_results
from mapswipe_workers import update_data
from mapswipe_workers.definitions import CustomError
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.definitions import logger
from mapswipe_workers.utils import slack

from mapswipe_workers.project_types.build_area.build_area_project \
        import BuildAreaProject
from mapswipe_workers.project_types.footprint \
        import FootprintProject


@click.command('create-projects')
@click.option('--schedule', default=None, help='')
def run_create_project(schedule):
    if schedule:
        if schedule == 'm':
            schedule.every(10).minutes.do(_run_create_projects)
            while True:
                schedule.run_pending()
                time.sleep(1)
        elif schedule == 'h':
            schedule.every().hour.do(_run_create_projects)
            while True:
                schedule.run_pending()
                time.sleep(1)
        elif schedule == 'd':
            schedule.every().day.do(_run_create_projects)
            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            pass
    else:
        _run_create_projects()


@click.command('transfer-results')
@click.option('--schedule', default=None, help='')
def run_transfer_results(schedule):
    if schedule:
        if schedule == 'm':
            schedule.every(10).minutes.do(_run_transfer_results)
            while True:
                schedule.run_pending()
                time.sleep(1)
        elif schedule == 'h':
            schedule.every().hour.do(_run_transfer_results)
            while True:
                schedule.run_pending()
                time.sleep(1)
        elif schedule == 'd':
            schedule.every().day.do(_run_transfer_results)
            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            pass
    else:
        _run_transfer_results()


@click.command('generate-stats')
@click.option('--schedule', default=None, help='')
def run_generate_stats(schedule):
    if schedule:
        if schedule == 'm':
            schedule.every(10).minutes.do(_run_generate_stats)
            while True:
                schedule.run_pending()
                time.sleep(1)
        elif schedule == 'h':
            schedule.every().hour.do(_run_generate_stats)
            while True:
                schedule.run_pending()
                time.sleep(1)
        elif schedule == 'd':
            schedule.every().day.do(_run_generate_stats)
            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            pass
    else:
        _run_generate_stats()


def _run_create_projects():
    project_types = {
            # Make sure to import all project types here
            1: BuildAreaProject,
            2: FootprintProject
            }
    project_type_names = {
            1: 'Build Area',
            2: 'Footprint'
            }

    fb_db = auth.firebaseDB()
    ref = fb_db.reference('projectDrafts/')
    project_drafts = ref.get()

    if project_drafts is None:
        return None

    created_project_ids = list()

    for project_draft_id, project_draft in project_drafts.items():
        project_draft['projectDraftId'] = project_draft_id
        # Early projects have no projectType attribute.
        # If so it defaults to 1
        project_type = project_draft.get('projectType', 1)
        try:
            # TODO: Document properly
            project = project_types[project_type](project_draft)
            if project.create_project(fb_db):
                created_project_ids.append(project.projectId)
                # delete project draft from firebase after
                # successfull project creation
                ref = fb_db.reference(f'projectDrafts/{project_draft_id}')
                ref.set({})
                newline = '\n'
                message = (
                        f'### PROJECT CREATION SUCCESSFUL ###{newline}'
                        f'Project Name: {project.name}{newline}'
                        f'Project Id: {project.projectId}{newline}'
                        f'Project Type: {project_type_names[project_type]}'
                        f'{newline}'
                        f'Make sure to activate the project in firebase.'
                        f'{newline}'
                        f'Happy Swiping. :)'
                        )
                slack.send_slack_message(message)
                logger.info(message)
        except CustomError:
            logger.exception(
                f'{project_draft_id} '
                f'- project creation failed'
                )
            continue
    return created_project_ids


def _run_transfer_results():
    update_data.update_user_data()
    update_data.update_project_data()
    transfer_results.transfer_results()


def _run_generate_stats():
    if not os.path.isdir(DATA_PATH):
        os.mkdir(DATA_PATH)

    data = generate_stats.generate_stats()
    filename = f'{DATA_PATH}/stats.json'
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    logger.info('exported stats')

    data = generate_stats.get_all_active_projects()
    filename = f'{DATA_PATH}/active_projects.json'
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    logger.info('exported stats')

    data = generate_stats.get_aggregated_results()
    filename = f'{DATA_PATH}/aggregated_results.json'
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    logger.info('exported aggregated results')


if __name__ == '__main__':

    schedule.every().hour.do(run_create_project)

    while True:
        schedule.run_pending()
        time.sleep(1)
