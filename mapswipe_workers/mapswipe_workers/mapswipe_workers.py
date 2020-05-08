"""Command Line Interface for MapSwipe Workers."""

import ast
import json
import time

import schedule as sched

import click
from mapswipe_workers import auth
from mapswipe_workers.definitions import CustomError, logger, sentry
from mapswipe_workers.firebase_to_postgres import (
    archive_project,
    delete_project,
    transfer_results,
    update_data,
)
from mapswipe_workers.generate_stats import generate_stats
from mapswipe_workers.project_types.build_area import build_area_tutorial
from mapswipe_workers.project_types.build_area.build_area_project import (
    BuildAreaProject,
)
from mapswipe_workers.project_types.change_detection import change_detection_tutorial
from mapswipe_workers.project_types.footprint.footprint_project import FootprintProject
from mapswipe_workers.utils import user_management
from mapswipe_workers.utils.create_directories import create_directories
from mapswipe_workers.utils.slack_helper import send_slack_message


class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            logger.exception(e)
            raise click.BadParameter(value)


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable logging.")
def cli(verbose):
    create_directories()
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

    project_type_classes = {
        1: BuildAreaProject,
        2: FootprintProject,
        3: BuildAreaProject,
        4: BuildAreaProject,
    }

    fb_db = auth.firebaseDB()
    ref = fb_db.reference("v2/projectDrafts/")
    project_drafts = ref.get()

    if project_drafts is None:
        logger.info("There are no project drafts in firebase.")
        return None

    for project_draft_id, project_draft in project_drafts.items():
        project_draft["projectDraftId"] = project_draft_id
        project_type = project_draft["projectType"]
        project_name = project_draft["name"]
        try:
            # Create a project object using appropriate class (project type).
            project = project_type_classes[project_type](project_draft)
            project.geometry = project.validate_geometries()
            project.create_groups()
            project.calc_required_results()
            # Save project and its groups and tasks to Firebase and Postgres.
            project.save_project()
            send_slack_message("success", project_name, project.projectId)
            logger.info("Success: Project Creation ({0})".format(project_name))
        except CustomError:
            ref = fb_db.reference(f"v2/projectDrafts/{project_draft_id}")
            ref.set({})
            send_slack_message("fail", project_name, project.projectId)
            logger.exception("Failed: Project Creation ({0}))".format(project_name))
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
        """ '["project_a", "project_b"]' """
    ),
)
def run_generate_stats(project_ids: list) -> None:
    """
    This is the wrapper function to generate statistics for given project ids.
    We do it this way, to be able to use --verbose flag
    for the _run_generate_stats function.
    Otherwise we can't use --verbose during run function.
    """
    _run_generate_stats(project_ids)


def _run_generate_stats(project_ids: list) -> None:
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
    except Exception:
        logger.exception()
        sentry.capture_exception()


@cli.command("create-tutorial")
@click.option(
    "--input-file", help=(f"A JSON file of the tutorial."), required=True, type=str,
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
    except Exception:
        logger.exception("sorry")
        sentry.capture_exception()


@cli.command("archive")
@click.option(
    "--project-id", "-i", help=("Archive project with giving project id"), type=str,
)
@click.option(
    "--project-ids",
    cls=PythonLiteralOption,
    default="[]",
    help=(
        f"Archive multiple projects. "
        f"Provide project id strings as a list: "
        f"""["project_a", "project_b"]"""
    ),
)
def run_archive_project(project_id, project_ids):
    """Archive projects in Postgres. Delete groups, tasks and results from Firebase."""
    if not project_ids and not project_id:
        click.echo("Missing argument")
        return None
    elif not project_ids:
        project_ids = [project_id]
    click.echo("Start archive")
    update_data.update_project_data(project_ids)
    transfer_results.transfer_results(project_ids)
    if archive_project.archive_project(project_ids):
        click.echo("Finished archive")


@cli.command("delete")
@click.option(
    "--project-id", "-i", help=("Delete project with giving project id"), type=str,
)
@click.option(
    "--project-ids",
    cls=PythonLiteralOption,
    default="[]",
    help=(
        f"Delete multiple projects. "
        f"Provide project id strings as a list: "
        f"""["project_a", "project_b"]"""
    ),
)
def run_delete_project(project_id, project_ids):
    """Delete tasks, groups, project and results."""
    if not project_ids and not project_id:
        click.echo("Missing argument")
        return None
    elif not project_ids:
        project_ids = [project_id]

    click.echo(
        "Projects and all associated data including results "
        + "with following project ids will be deleted permantly:"
    )
    for project_id in project_ids:
        click.echo(project_id)
    click.echo()
    click.echo("Continue with deletion? [y/n] ", nl=False)
    click.echo()
    c = click.getchar()

    if c == "y":
        click.echo("Start deletion")
        if delete_project.delete_project(project_ids):
            click.echo("Finished deletions")
    elif c == "n":
        click.echo("Abort!")
    else:
        click.echo("Invalid input")


@cli.command("run")
@click.option("--schedule", is_flag=True, help="Schedule jobs to run every 10 minutes.")
@click.pass_context
def run(context, schedule):
    """
    Run all commands.

    Run --create-projects, --firebase-to-postgres and --generate_stats_all_projects.
    If schedule option is set above commands will be run every 10 minutes sequentially.
    """

    def _run():
        logger.info("start mapswipe backend workflow.")
        context.invoke(run_create_projects)
        project_ids = context.invoke(run_firebase_to_postgres)
        context.invoke(run_generate_stats, project_ids=project_ids)

    if schedule:
        sched.every(10).minutes.do(_run).run()
        while True:
            sched.run_pending()
            time.sleep(1)
    else:
        _run()
