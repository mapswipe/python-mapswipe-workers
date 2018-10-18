from mapswipe_workers.projects import BuildAreaProject as b
from mapswipe_workers.projects import FootprintProject as f

def init_project(project_type, project_id):

    class_to_type = {
        1: b.BuildAreaProject(project_id),
        2: f.FootprintProject(project_id)
    }
    proj = class_to_type[project_type]
    return proj


class BaseProject(object):
    # info is a dictionary with information about the project
    def __init__(self, project_id):
        # set basic project information
        self.id = project_id

    def set_project_info(self, info):

        self.name = info['name']
        self.image = info['image']
        self.import_key = info['importKey']

    ## We define a bunch of functions related to importing new projects
    def import_project(self, info, firebase, mysqlDB):
        print("start importing project: %s" % vars(self))
        self.set_project_info(info)
        self.create_groups()
        self.set_groups_firebase(firebase)
        self.set_project_mysql(mysqlDB)
        self.set_project_firebase(firebase)
        self.set_import_complete(firebase)
        print("finished importing project")

    def set_groups_firebase(self, firebase):
        print("set %s groups in firebase." % len(self.groups))

    def set_project_firebase(self, firebase):
        print("set project in firebase.")

    def set_project_mysql(self, mysqlDB):
        print("set project in mysql.")

    def set_import_complete(self, firebase):
        print("set import complete in firebase")

    # We define a bunch of functions related to deleting projects
    def delete_project(self, firebase, mysqlDB):
        self.delete_groups_firebase(firebase)
        self.delete_project_firebase(firebase)
        self.delete_project_mysql(mysqlDB)
        self.delete_import_firebase(firebase)
        print("deleted project")

    def delete_groups_firebase(self, firebase):
        print("deleted groups in firebase")

    def delete_project_firebase(self, firebase):
        print("deleted project in firebase")

    def delete_project_mysql(self, mysqlDB):
        print("deleted project in mysqlDB")

    def delete_import_firebase(self, firebase):
        print("deleted import in firebase")

    ## We define a bunch of functions related to updating existing projects
    def update_project(self, firebase, mysqlDB):
        self.get_progress(firebase)
        self.get_contributors(mysqlDB)
        self.set_progress(firebase)
        self.set_contributors(firebase)

    def get_progress(self, firebase):
        self.progress = 100
        print("got project progress from firebase")

    def get_contributors(self, mysqlDB):
        self.contributors = 55
        print("got project contributors from mysql")

    def set_progress(self, firebase):
        print("set project progress in firebase")

    def set_contributors(self, firebase):
        print("set project conributors in firebase")

    # We define a bunch of functions related to exporting exiting projects
    def export_to_json(self):
        project_json = 'some json'
        print("exported project as json")
        return project_json