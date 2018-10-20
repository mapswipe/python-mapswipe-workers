import logging


from mapswipe_workers.cfg import auth
# Make sure to import all project types here
from mapswipe_workers.ProjectTypes.BuildArea.BuildAreaProject import BuildAreaProject
from mapswipe_workers.ProjectTypes.Footprint.FootprintProject import FootprintProject


def init_project(project_type, project_id):

    class_to_type = {
        # Make sure to import all project types here
        1: BuildAreaProject(project_id),
        2: FootprintProject(project_id)
    }

    proj = class_to_type[project_type]
    return proj


def get_highest_project_id(firebase):
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

    highest_project_id = get_highest_project_id(firebase)
    # we add 2 to avoid firebase result being parsed as a list instead of json
    new_project_id = highest_project_id + 2
    return new_project_id


def get_new_imports(firebase):
    # this functions looks for new entries in the firebase importer table
    # the output is a dictionary with all information for newly imported projects


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


    # check for new imports in firebase
    # this will return a list of imports
    imports = get_new_imports(firebase)
    for import_key, new_import in imports.items():

        # let's create a project now
        project_id = get_new_project_id(firebase)

        # this will be the place, where we distinguish different project types

        proj = init_project(new_import['projectType'], project_id)
        if not proj:
            continue

        proj.import_project(import_key, new_import, firebase, mysqlDB)