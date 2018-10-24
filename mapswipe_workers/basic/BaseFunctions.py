import logging

from mapswipe_workers.cfg import auth
# Make sure to import all project types here
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaProject import BuildAreaProject
from mapswipe_workers.ProjectTypes.Footprint.FootprintProject import FootprintProject


def init_project(project_type, project_id):
    """
    The function to init a project in regard to its type

    Parameters
    ----------
    project_type : int
        the type of the project
    project_id: int
        the id of the project

    Returns
    -------
    proj :
        the project instance
    """

    class_to_type = {
        # Make sure to import all project types here
        1: BuildAreaProject(project_id),
        2: FootprintProject(project_id)
    }

    proj = class_to_type[project_type]
    return proj


def get_highest_project_id(firebase):
    """
    The function to get the highest project id from firebase

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    highest_project_id : int
        highest id of a project in firebase

    Notes
    -----
    If not project id is found in firebase (no project imported yes) the project id is set to 1000
    """

    fb_db = firebase.database()

    project_keys = fb_db.child('projects').shallow().get().val()
    if not project_keys:
        # set mininum project id to 1000, if no project has been imported yet
        project_keys = [1000]

    project_ids = list(map(int, list(project_keys)))
    project_ids.sort()
    highest_project_id = project_ids[-1]

    logging.warning('returned highest project id: %s' % highest_project_id)
    return highest_project_id


def get_new_project_id(firebase):
    """
    The function to get a project id which is not used in firebase

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    new_project_id : int
        a new project id which has not been used in firebase

    Notes
    -----
        the new project id needs to be increased by more than 1 to avoid firebase json parsed as an array
        more information here: https://firebase.googleblog.com/2014/04/best-practices-arrays-in-firebase.html
    """

    highest_project_id = get_highest_project_id(firebase)
    new_project_id = highest_project_id + 2
    return new_project_id


def get_new_imports(firebase):
    """
    The function to get new project imports from firebase which have not been imported

    Parameters
    ----------
    firebase : pyrebase firebase object
        initialized firebase app with admin authentication

    Returns
    -------
    new_imports : dict
        a dictionary of imports which have not been imported already
    """

    fb_db = firebase.database()
    all_imports = fb_db.child("imports").get().val()

    new_imports = {}
    if all_imports:
        for import_key, new_import in all_imports.items():
            try:
                # check if project was already imported and "complete" is set
                complete = new_import['complete']
            except:
                # insert into new projects dict
                new_imports[import_key] = new_import

    logging.warning('got %s projects which have not been imported' % len(new_imports))
    return new_imports


def run_import(modus):
    """
    A function to create all newly imported projects in firebase

    Parameters
    ----------
    modus : str
        either `development` or `production to decide which firebase configuration to use

    Returns
    -------
    imported_projects : list
        list of project ids of imported projects
    """

    if modus == 'development':
        # we use the dev instance for testing
        firebase = auth.dev_firebase_admin_auth()
        mysqlDB = auth.dev_mysqlDB
        print('We are using the development instance')
    elif modus == 'production':
        # we use the dev instance for testing
        firebase = auth.firebase_admin_auth()
        mysqlDB = auth.mysqlDB
        print('We are using the production instance')

    # this will return a list of imports
    imported_projects = []

    # check for new imports in firebase
    imports = get_new_imports(firebase)
    for import_key, new_import in imports.items():

        # let's create a project now
        project_id = get_new_project_id(firebase)
        try:
            project_type = new_import['projectType']
        except:
            project_type = 1

        # this will be the place, where we distinguish different project types
        proj = init_project(project_type, project_id)
        if not proj:
            continue

        if not proj.import_project(import_key, new_import, firebase, mysqlDB):
            print('something went wrong with project %s' % proj.id)
        else:
            imported_projects.append(project_id)

    return imported_projects
