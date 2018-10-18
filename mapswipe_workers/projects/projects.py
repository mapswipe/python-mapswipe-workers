def init_project(project_type, project_id):

    class_to_type = {
        1: BuildAreaProject(project_id),
        2: FootprintProject(project_id)
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


########################################################################################################################
# A Build Area Project
class BuildAreaProject(BaseProject):
    type = 1

    def __init__(self, project_id):
        # super() executes fine now
        super(BuildAreaProject, self).__init__(project_id)

    def set_project_info(self, info):
        super(BuildAreaProject, self).set_project_info(info)
        self.info = {
            "tileserver": info['tileserver'],
            "zoomlevel": info['zoomlevel'],
            "extent": info['extent']
        }

    def create_groups(self):
        groups = {}
        for i in range(0, 3):
            groups[i] = BuildAreaGroup(self, i)
        self.groups = groups


########################################################################################################################
# A Footprint Project
class FootprintProject(BaseProject):
    type = 2

    def __init__(self, project_id):
        # super() executes fine now
        super(FootprintProject, self).__init__(project_id)

    def set_project_info(self, info):
        super(FootprintProject, self).set_project_info(info)
        self.info = {
            "tileserver_url": info['tileserver_url'],
            "input_geometries": info['input_geometries']
        }

    def create_groups(self):
        groups = {}
        # here we create the groups according to the workflow of the project type
        for i in range(0, 3):
            groups[i] = FootprintGroup(self, i)
        self.groups = groups




# We define a bunch of functions to work with projects
def get_new_imports_old():

    import1 = {
        "importKey" : "key 1",
        "type" : 1,
        "id": 123,
        "name": 'proj1',
        "image": 'some image.png',
        "tileserver": "bing",
        "zoomlevel": 18,
        "verificationCount": 3,
        "extent": ".data/project_1_geom.kml"
    }

    import2 = {
        "importKey": "key 2",
        "type": 2,
        "id": 234,
        "name": "proj2",
        "image": "another image.png",
        "tileserver_url": "http://tileserver.xyz",
        "input_geometries": "./data/builing_footprints_tanzania.geojson",
        "verificationCount": 3
    }

    import2 = {
        "importKey": "key 1",
        "type": 1,
        "id": 123,
        "name": 'proj3',
        "image": 'some image.png',
        "tileserver": "bing",
        "zoomlevel": 18,
        "verificationCount": 3,
        "extent": ".data/project_1_geom.kml"
    }

    imports = [import1, import2]
    return imports


def get_new_imports(firebase):
    # this functions looks for new entries in the firebase importer table
    # the output is a dictionary with all information for newly imported projects

    new_imports = {}
    fb_db = firebase.database()

    # iterate over all the keys in the importer, add the ones to the importer cache that are not yet complete
    all_imports = fb_db.child("imports").child("complete").equal_to(None).get().val()

    db.child("users").order_by_child("score").equal_to(10).get()


    if all_imports:
        for import_key, project in all_imports.items():
            try:
                # check if project was already imported and "complete" is set
                complete = project['complete']
            except:
                # insert into new projects dict
                new_imports[import_key] = project

    return new_imports