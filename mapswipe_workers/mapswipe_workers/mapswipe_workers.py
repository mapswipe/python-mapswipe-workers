"""Command Line Interface for MapSwipe Workers."""

import ast
import time

import click
import schedule as sched

from mapswipe_workers import auth
from mapswipe_workers.definitions import (
    CustomError,
    MessageType,
    ProjectType,
    logger,
    sentry,
)
from mapswipe_workers.firebase_to_postgres import (
    archive_project,
    delete_project,
    transfer_results,
    update_data,
)
from mapswipe_workers.generate_stats import generate_stats
from mapswipe_workers.utils import team_management, user_management
from mapswipe_workers.utils.create_directories import create_directories
from mapswipe_workers.utils.slack_helper import (
    send_progress_notification,
    send_slack_message,
)


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
    else:
        logger.info("Logging enabled")


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
        logger.info("There are no project drafts in firebase.")
        return None

    for project_draft_id, project_draft in project_drafts.items():
        project_draft["projectDraftId"] = project_draft_id
        project_type = project_draft["projectType"]
        project_name = project_draft["name"]
        try:
            # Create a project object using appropriate class (project type).
            project = ProjectType(project_type).constructor(project_draft)
            # TODO: here the project.geometry attribute is overwritten
            #  this is super confusing since it's not a geojson anymore
            #  but this is what we set initially,
            #  e.g. in tile_map_service_grid/project.py
            #  project.geometry is set to a list of wkt geometries now
            #  this can't be handled in postgres,
            #  postgres expects just a string not an array
            #  validated_geometries should be called during init already
            #  for the respective project types
            project.geometry = project.validate_geometries()
            project.create_groups()
            project.calc_required_results()
            # Save project and its groups and tasks to Firebase and Postgres.
            project.save_project()
            send_slack_message(MessageType.SUCCESS, project_name, project.projectId)
            logger.info("Success: Project Creation ({0})".format(project_name))
        except CustomError as e:
            ref = fb_db.reference(f"v2/projectDrafts/{project_draft_id}")
            ref.set({})
            send_slack_message(
                MessageType.FAIL, project_name, project.projectId, str(e)
            )
            logger.exception("Failed: Project Creation ({0}))".format(project_name))
            sentry.capture_exception()
        continue


@cli.command("firebase-to-postgres")
def run_firebase_to_postgres() -> list:
    """Update users and transfer results from Firebase to Postgres."""
    update_data.update_user_data()
    update_data.update_project_data()
    project_ids = transfer_results.transfer_results()
    for project_id in project_ids:
        send_progress_notification(project_id)
    return project_ids


@cli.command("generate-stats")
@click.option(
    "--project_ids",
    cls=PythonLiteralOption,
    default="[]",
    help=(
        "Project ids for which to generate stats as a list of strings: "
        """ '["project_a", "project_b"]' """
        "(You need the quotes.)"
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
@click.option("--email", help="The email of the MapSwipe user.", type=str)
@click.option(
    "--emails",
    cls=PythonLiteralOption,
    default="[]",
    help=(
        "The emails of the MapSwipe users as a list of strings: "
        """ '["email_a", "email_b"]' """
        "(You need the quotes.)"
    ),
)
@click.option("--team_id", "-i", help="The id of the team in Firebase.", type=str)
@click.option(
    "--action",
    "-a",
    help=(
        "You can either add, remove manager-rights or "
        "add, remove user to/from a team. "
        "choices here"
    ),
    type=click.Choice(
        ["add-manager-rights", "remove-manager-right", "add-team", "remove-team"]
    ),
)
def run_user_management(email, emails, action, team_id) -> None:
    """
    Manage project manager credentials

    Grant or remove credentials.
    """
    if email:
        email_list = [email]
    else:
        email_list = emails

    for email in email_list:
        try:
            if action == "add-manager-rights":
                user_management.set_project_manager_rights(email)
            elif action == "remove-manager-rights":
                user_management.remove_project_manager_rights(email)
            elif action == "add-team":
                if not team_id:
                    click.echo("Missing argument: --team_id")
                    return None
                user_management.add_user_to_team(email, team_id)
            elif action == "remove-team":
                user_management.remove_user_from_team(email)
        except Exception:
            logger.exception("grant user credentials failed")
            sentry.capture_exception()


@cli.command("team-management")
@click.option(
    "--team_name",
    "-n",
    help="The name of the team in Firebase for creation.",
    type=str,
)
@click.option("--team_id", "-i", help="The id of the team in Firebase.", type=str)
@click.option(
    "--action",
    "-a",
    help=(
        "You can either create, delete teams or renew the teamToken. " "choices here"
    ),
    type=click.Choice(
        ["create", "delete", "renew-team-token", "remove-all-team-members"]
    ),
)
def run_team_management(team_name, team_id, action) -> None:
    """Create, Delete Teams or Renew TeamToken."""
    try:
        if action == "create":
            if not team_name:
                click.echo("Missing argument: --team_name")
                return None
            else:
                team_management.create_team(team_name)
        elif action == "delete":
            if not team_id:
                click.echo("Missing argument: --team_id")
                return None
            else:
                click.echo(
                    f"Do you want to delete the team with the id: {team_id}? [y/n] ",
                    nl=False,
                )
                click.echo()
                c = click.getchar()
                if c == "y":
                    click.echo("Start deletion")
                    team_management.delete_team(team_id)
                elif c == "n":
                    click.echo("Abort!")
                else:
                    click.echo("Invalid input")
        elif action == "renew-team-token":
            if not team_id:
                click.echo("Missing argument: --team_id")
                return None
            else:
                team_management.renew_team_token(team_id)
        elif action == "remove-all-team-members":
            if not team_id:
                click.echo("Missing argument: --team_id")
                return None
            else:
                click.echo(
                    f"Do you want to remove all users from "
                    f"the team with the id: {team_id}? [y/n] ",
                    nl=False,
                )
                click.echo()
                c = click.getchar()
                if c == "y":
                    click.echo("Start remove all team members")
                    team_management.remove_all_team_members(team_id)
                elif c == "n":
                    click.echo("Abort!")
                else:
                    click.echo("Invalid input")
    except Exception:
        logger.exception("team management failed")
        sentry.capture_exception()


@cli.command("create-tutorials")
def run_create_tutorials() -> None:
    fb_db = auth.firebaseDB()
    ref = fb_db.reference("v2/tutorialDrafts/")
    tutorial_drafts = ref.get()

    if tutorial_drafts is None:
        logger.info("There are no tutorial drafts in firebase.")
        return None

    for tutorial_draft_id, tutorial_draft in tutorial_drafts.items():
        tutorial_draft["tutorialDraftId"] = tutorial_draft_id
        project_type = tutorial_draft["projectType"]
        project_name = tutorial_draft["name"]

        try:
            tutorial = ProjectType(project_type).tutorial(tutorial_draft)
            tutorial.create_tutorial_groups()
            tutorial.create_tutorial_tasks()
            tutorial.save_tutorial()
            send_slack_message(MessageType.SUCCESS, project_name, tutorial.projectId)
            logger.info(f"Success: Tutorial Creation ({project_name})")
        except CustomError:
            ref = fb_db.reference(f"v2/tutorialDrafts/{tutorial_draft_id}")
            ref.set({})
            send_slack_message(MessageType.FAIL, project_name, tutorial.projectId)
            logger.exception("Failed: Project Creation ({0}))".format(project_name))
            sentry.capture_exception()
        continue


@cli.command("archive")
@click.option(
    "--project-id", "-i", help=("Archive project with giving project id"), type=str,
)
@click.option(
    "--project-ids",
    cls=PythonLiteralOption,
    default="[]",
    help=(
        "Archive multiple projects. "
        "Provide project id strings as a list: "
        """'["project_a", "project_b"]'"""
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
        "Delete multiple projects. "
        "Provide project id strings as a list: "
        """'["project_a", "project_b"]'"""
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
        context.invoke(run_create_tutorials)
        project_ids = context.invoke(run_firebase_to_postgres)
        context.invoke(run_generate_stats, project_ids=project_ids)

    if schedule:
        sched.every(10).minutes.do(_run).run()
        while True:
            sched.run_pending()
            time.sleep(1)
    else:
        _run()
