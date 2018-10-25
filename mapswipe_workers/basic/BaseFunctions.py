import logging

from mapswipe_workers.cfg import auth
# Make sure to import all project types here
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaProject import BuildAreaProject
from mapswipe_workers.ProjectTypes.Footprint.FootprintProject import FootprintProject


########################################################################################################################
# INIT                                                                                                                 #
########################################################################################################################
def get_environment(modus):

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
    else:
        firebase = None
        mysqlDB = None

    return firebase, mysqlDB

def init_project(project_type, project_id, firebase, mysqlDB, import_key=None, import_dict=None):
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
        1: BuildAreaProject(project_id, firebase, mysqlDB, import_key, import_dict),
        # 2: FootprintProject(project_id, firebase, import_key, import_dict)
    }

    proj = class_to_type[project_type]
    return proj


def get_projects(firebase, mysqlDB, filter='all'):

    # create a list for projects according to filter
    projects_list = []

    fb_db = firebase.database()
    all_projects = fb_db.child("projects").get().val()

    # we need to check if the user provided a list of project ids to filter
    if type(filter) is list:
        project_ids = filter.copy()
        filter = 'user'
    else:
        project_ids = []

    for project_id in all_projects:
        # we check all conditions for each group of projects
        conditions = {
            'all': True,
            'active': all_projects[project_id]['state'] == 0,
            'not_finished': all_projects[project_id]['progress'] < 100,
            'user': int(project_id) in project_ids
        }

        if conditions[filter]:
            try:
                project_type = all_projects[project_id]['projectType']
            except:
                project_type = 1
            proj = init_project(project_type, project_id, firebase, mysqlDB)
            projects_list.append(proj)

    return projects_list


########################################################################################################################
# IMPORT                                                                                                               #
########################################################################################################################
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

    fb_db = firebase.database()

    project_keys = fb_db.child('projects').shallow().get().val()
    if not project_keys:
        # set mininum project id to 1000, if no project has been imported yet
        project_keys = [1000]

    project_ids = list(map(int, list(project_keys)))
    project_ids.sort()
    highest_project_id = project_ids[-1]

    logging.warning('highest existing project id: %s' % highest_project_id)
    new_project_id = highest_project_id + 2

    logging.warning('returned new project id: %s' % highest_project_id)
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

    # get dev or production environment for firebase and mysql
    firebase, mysqlDB = get_environment(modus)

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
        proj = init_project(project_type, project_id, firebase, mysqlDB, import_key, new_import)
        proj.import_project(firebase, mysqlDB)
        imported_projects.append(proj.id)

    return imported_projects


########################################################################################################################
# UPDATE                                                                                                               #
########################################################################################################################
def run_update(modus, filter, output_path):
    """
    The function to update project progress and contributors in firebase

    Parameters
    ----------
    modus : str
        The environment to use for firebase and mysql
        Can be either 'development' or 'production'
    filter : str or list
        The filter for the projects.
        Can be either 'all', 'active', 'not_finished' or a list of project ids as integer
    output_path: str
        The output path of the logs for progress and contributors

    Returns
    -------
    updated_projects : list
        The list of all projects ids for projects which have been updated
    """

    # get dev or production environment for firebase and mysql
    firebase, mysqlDB = get_environment(modus)

    project_list = get_projects(firebase, filter)
    updated_projects = []
    for proj in project_list:
        proj.update_project(firebase, mysqlDB, output_path)
        updated_projects.append(proj.id)

    return updated_projects


########################################################################################################################
# TRANSFER RESULTS                                                                                                     #
########################################################################################################################
def run_transfer_results():
    pass

########################################################################################################################
# EXPORT                                                                                                               #
########################################################################################################################
def run_export():
    pass