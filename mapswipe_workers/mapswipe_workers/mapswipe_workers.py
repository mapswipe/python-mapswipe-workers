import time
import click
import schedule as sched
import pickle

from mapswipe_workers.definitions import CustomError
from mapswipe_workers.definitions import logger
from mapswipe_workers.utils import slack
from mapswipe_workers.utils import sentry

from mapswipe_workers import auth
from mapswipe_workers.generate_stats import generate_stats
from mapswipe_workers.firebase_to_postgres import transfer_results
from mapswipe_workers.firebase_to_postgres import update_data
from mapswipe_workers.project_types.build_area.build_area_project \
        import BuildAreaProject
from mapswipe_workers.project_types.footprint.footprint_project \
        import FootprintProject
from mapswipe_workers.project_types.change_detection.change_detection_project \
        import ChangeDetectionProject
from mapswipe_workers.utils import user_management

@click.group()
@click.option(
        '--verbose',
        '-v',
        is_flag=True,
        )
@click.version_option()
def cli(verbose):
    if not verbose:
        logger.disabled = True


@click.command('create-projects')
@click.option(
        '--schedule',
        '-s',
        default=None,
        help=(
            f'Will create projects every '
            f'10 minutes (m), every hour (h) or every day (d). '
            ),
        type=click.Choice(['m', 'h', 'd'])
        )
def run_create_projects(schedule):
    sentry.init_sentry()
    try:
        if schedule:
            if schedule == 'm':
                sched.every(10).minutes.do(_run_create_projects)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            elif schedule == 'h':
                sched.every().hour.do(_run_create_projects)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            elif schedule == 'd':
                sched.every().day.do(_run_create_projects)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            else:
                click.echo(
                        f'{schedule} is not a valid input '
                        f'for the schedule argument. '
                        f'Use m for every 10 minutes, '
                        f'h for every hour and d for every day.'
                        )
        else:
            _run_create_projects()
    except Exception as e:
        slack.send_error(e)
        sentry.capture_exception_sentry(e)
        logger.exception(e)


@click.command('firebase-to-postgres')
@click.option(
        '--schedule',
        '-s',
        default=None,
        help=(
            f'Will update and transfer relevant data (i.a. users and results) '
            f'from Firebase into Postgres '
            f'every 10 minutes (m), every hour (h) or every day (d). '
            ),
        type=click.Choice(['m', 'h', 'd'])
        )
def run_firebase_to_postgres(schedule):
    sentry.init_sentry()
    try:
        if schedule:
            if schedule == 'm':
                sched.every(10).minutes.do(_run_firebase_to_postgres)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            elif schedule == 'h':
                sched.every().hour.do(_run_firebase_to_postgres)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            elif schedule == 'd':
                sched.every().day.do(_run_firebase_to_postgres)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            else:
                click.echo(
                        f'{schedule} is not a valid input '
                        f'for the schedule argument. '
                        f'Use m for every 10 minutes, '
                        f'h for every hour and d for every day.'
                        )
        else:
            _run_firebase_to_postgres()
    except Exception as e:
        slack.send_error(e)
        sentry.capture_exception_sentry(e)
        logger.exception(e)


@click.command('generate-stats')
@click.option(
        '--schedule',
        '-s',
        default=None,
        help=(
            f'Will generate stats every '
            f'10 minutes (m), every hour (h) or every day (d). '
            ),
        type=click.Choice(['m', 'h', 'd'])
        )
@click.option(
        '--only_new_results/--all',
        default=False,
        help=(
            f'Will generate stats only for projects and users'
            f'for which new results have been transfered.'
            )
        )
def run_generate_stats(schedule, only_new_results):
    sentry.init_sentry()
    try:
        if schedule:
            if schedule == 'm':
                sched.every(10).minutes.do(_run_generate_stats)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            elif schedule == 'h':
                sched.every().hour.do(_run_generate_stats)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            elif schedule == 'd':
                sched.every().day.do(_run_generate_stats)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            else:
                click.echo(
                        f'{schedule} is not a valid input '
                        f'for the schedule argument. '
                        f'Use m for every 10 minutes, '
                        f'h for every hour and d for every day.'
                        )
        else:
            _run_generate_stats(only_new_results)
    except Exception as e:
        slack.send_error(e)
        sentry.capture_exception_sentry(e)
        logger.exception(e)

@click.command('user-management')
@click.option(
        '--email',
        help=(
            f'The email of the MapSwipe user.'
            ),
        required=True,
        type=str
        )
@click.option(
        '--manager',
        help=(
            f'Set option to grant or remove project manager credentials. '
            f'Use true to grant credentials. '
            f'Use false to remove credentials. '
            ),
        type=bool
        )
def run_user_management(email, manager):
    sentry.init_sentry()
    try:
        if email:
            _run_user_management(email, manager)
        else:
            click.echo(
                f'Please provide all required input arguments.'
            )
    except Exception as e:
        slack.send_error(e)
        sentry.capture_exception_sentry(e)
        logger.exception(e)


@click.command('run')
@click.option(
        '--schedule',
        '-s',
        default=None,
        help=(
            f'Will run Mapswipe Workers every '
            f'10 minutes (m), every hour (h) or every day (d). '
            ),
        type=click.Choice(['m', 'h', 'd'])
        )
def run(schedule):
    sentry.init_sentry()
    try:
        if schedule:
            if schedule == 'm':
                sched.every(10).minutes.do(_run_create_projects)
                sched.every(10).minutes.do(_run_firebase_to_postgres)
                sched.every(10).minutes.do(_run_generate_stats)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            elif schedule == 'h':
                sched.every().hour.do(_run_create_projects)
                sched.every().hour.do(_run_firebase_to_postgres)
                sched.every().hour.do(_run_generate_stats)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            elif schedule == 'd':
                sched.every().day.do(_run_create_projects)
                sched.every().day.do(_run_firebase_to_postgres)
                sched.every().day.do(_run_generate_stats)
                while True:
                    sched.run_pending()
                    time.sleep(1)
            else:
                click.echo(
                        f'{schedule} is not a valid input '
                        f'for the schedule argument. '
                        f'Use m for every 10 minutes, '
                        f'h for every hour and d for every day.'
                        )
        else:
            _run_create_projects()
            _run_firebase_to_postgres()
            _run_generate_stats()
    except Exception as e:
        slack.send_error(e)
        sentry.capture_exception_sentry(e)
        logger.exception(e)


def _run_create_projects(project_draft_ids=None):
    project_types = {
            # Make sure to import all project types here
            1: BuildAreaProject,
            2: FootprintProject,
            3: ChangeDetectionProject
            }
    project_type_names = {
            1: 'Build Area',
            2: 'Footprint',
            3: 'Change Detection'
            }

    fb_db = auth.firebaseDB()
    ref = fb_db.reference('v2/projectDrafts/')
    project_drafts = ref.get()

    if project_drafts is None:
        del(fb_db)
        return None

    else:
        created_project_ids = list()

        for project_draft_id, project_draft in project_drafts.items():
            project_draft['projectDraftId'] = project_draft_id

            # filter out project which are not in project_ids list
            # this is only done if a list is provided

            if project_draft_ids:
                if project_draft_id not in project_draft_ids:
                    # pass projects that are not in provided list
                    continue

            # Early projects have no projectType attribute.
            # If so it defaults to 1
            project_type = project_draft.get('projectType', 1)
            try:
                # TODO: Document properly
                project = project_types[project_type](project_draft)
                project.geometry = project.validate_geometries()
                project.create_groups()
                project.calc_required_results()
                if project.save_project(fb_db):
                    created_project_ids.append(project.projectId)
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
                newline = '\n'
                message = (
                    f'### PROJECT CREATION FAILED ###{newline}'
                    f'Project Name: {project_draft["name"]}{newline}'
                    f'Project Id: {project_draft_id}{newline}'
                    f'{newline}'
                    f'Please check what went wrong.'
                )
                slack.send_slack_message(message)
                slack.send_error(CustomError)
                logger.exception(
                    f'{project_draft_id} '
                    f'- project creation failed'
                    )
                continue
    del(fb_db)
    return created_project_ids


def _run_firebase_to_postgres():
    update_data.update_user_data()
    update_data.update_project_data()
    transfer_results.transfer_results()


def _run_generate_stats(only_new_results):
    generate_stats(only_new_results)


def _run_user_management(email, manager):
    if manager is not None:
        if manager:
            user_management.set_project_manager_rights(email)
        else:
            user_management.remove_project_manager_rights(email)


cli.add_command(run_create_projects)
cli.add_command(run_firebase_to_postgres)
cli.add_command(run_generate_stats)
cli.add_command(run_user_management)
cli.add_command(run)
