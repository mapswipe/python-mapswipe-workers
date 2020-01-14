"""Command Line Interface for MapSwipe Workers."""

import ast
import json
import time

import click
import schedule as sched
from mapswipe_workers import auth
from mapswipe_workers.definitions import (
    PROJECT_TYPE_CLASSES,
    PROJECT_TYPE_NAMES,
    CustomError,
    logger,
)
from mapswipe_workers.firebase_to_postgres import transfer_results, update_data
from mapswipe_workers.generate_stats import generate_stats
from mapswipe_workers.project_types.build_area import build_area_tutorial
from mapswipe_workers.project_types.change_detection import change_detection_tutorial
from mapswipe_workers.utils import sentry, slack, user_management


class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            logger.exception(e)
            raise click.BadParameter(value)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable logging.")
@click.version_option()
def cli(verbose):
    """Enable logging."""
    if not verbose:
        logger.disabled = True


@cli.command("create-projects")
def run_create_projects():
    """
    Create projects from submitted project drafts.

    Get project drafts from Firebase.
    Create projects with groups and tasks.
    Save created projects, groups and tasks to Firebase and Postgres.
    """
    fb_db = auth.firebaseDB()
    ref = fb_db.reference("v2/projectDrafts/")
    project_drafts = ref.get()

    if project_drafts is None:
        return None

    for project_draft_id, project_draft in project_drafts.items():
        project_draft["projectDraftId"] = project_draft_id
        project_type = project_draft["projectType"]
        try:
            # Create a project object using appropriate class (project type).
            project = PROJECT_TYPE_CLASSES[project_type](project_draft)
            project.geometry = project.validate_geometries()
            project.create_groups()
            project.calc_required_results()
            # Save project and its groups and tasks to Firebase and Postgres.
            project.save_project()
            newline = "\n"
            message = (
                f"### PROJECT CREATION SUCCESSFUL ###{newline}"
                f"Project Name: {project.name}{newline}"
                f"Project Id: {project.projectId}{newline}"
                f"Project Type: {PROJECT_TYPE_NAMES[project_type]}"
                f"{newline}"
                f"Make sure to activate the project "
                f"using the manager dashboard."
                f"{newline}"
                f"Happy Swiping. :)"
            )
            slack.send_slack_message(message)
            logger.info(message)
        except CustomError:
            ref = fb_db.reference(f"v2/projectDrafts/{project_draft_id}")
            ref.set({})
            newline = "\n"
            message = (
                f"### PROJECT CREATION FAILED ###{newline}"
                f'Project Name: {project_draft["name"]}{newline}'
                f"Project Id: {project_draft_id}{newline}"
                f"{newline}"
                f"Project draft is deleted.{newline}"
                f"Please check what went wrong."
            )
            slack.send_slack_message(message)
            slack.send_error(CustomError)
            logger.exception(f"{project_draft_id} " f"- project creation failed")
            sentry.capture_exception()
            continue


@cli.command("firebase-to-postgres")
def run_firebase_to_postgres() -> list:
    """Update users and transfer results from Firebase to Postgres."""
    update_data.update_user_data()
    update_data.update_project_data()
    project_ids = transfer_results.transfer_results()
    return project_ids


@cli.command("generate-stats")
@click.option(
    "--project_ids",
    cls=PythonLiteralOption,
    default="[]",
    help=(
        "Project ids for which to generate stats as a list of strings: "
        + """["project_a", "project_b"]"""
    ),
)
def run_generate_stats(project_ids: list) -> None:
    """Generate statistics for given project ids."""
    generate_stats.generate_stats(project_ids)


@cli.command("generate-stats-all-projects")
def run_generate_stats_all_projects() -> None:
    """Generate statistics for all projects."""
    generate_stats.generate_stats_all_projects()


@cli.command("user-management")
@click.option(
    "--email", help=(f"The email of the MapSwipe user."), required=True, type=str
)
@click.option(
    "--manager",
    help=("Use true to grant credentials. Use false to remove credentials."),
    type=bool,
)
def run_user_management(email, manager) -> None:
    """
    Manage project manager credentials

    Grant or remove credentials.
    """
    try:
        if manager:
            user_management.set_project_manager_rights(email)
        elif not manager:
            user_management.remove_project_manager_rights(email)
    except Exception as e:
        slack.send_error(e)
        sentry.capture_exception_sentry(e)
        logger.exception(e)


@cli.command("create-tutorial")
@click.option(
    "--input-file",
    help=(f"A JSON file of the tutorial."),
    required=True,
    type=click.Path,
)
def run_create_tutorial(input_file) -> None:
    """Create a tutorial project from provided JSON file."""
    try:
        logger.info(f"will generate tutorial based on {input_file}")
        with open(input_file) as json_file:
            tutorial = json.load(json_file)

        project_type = tutorial["projectType"]

        project_types_tutorial = {
            # Make sure to import all project types here
            1: build_area_tutorial.create_tutorial,
            3: change_detection_tutorial.create_tutorial,
        }

        project_types_tutorial[project_type](tutorial)
    except Exception as e:
        slack.send_error(e)
        sentry.capture_exception_sentry(e)
        logger.exception(e)


@cli.command("run")
@click.option(
    "--schedule", is_flag=True, help=("Schedule jobs to run every 10 minutes.")
)
def run(schedule: bool) -> None:
    """
    Run all commands.

    Run --create-projects, --firebase-to-postgres and --generate_stats_all_projects.
    If schedule option is set above commands will be run every 10 minutes sequentially.
    """

    def _run():
        run_create_projects()
        project_ids = run_firebase_to_postgres()
        run_generate_stats(project_ids)

    if schedule:
        sched.every(10).minutes.do(_run)
        while True:
            sched.run_pending()
            time.sleep(1)
    else:
        _run()
