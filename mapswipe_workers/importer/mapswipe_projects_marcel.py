def get_new_imports():

    import1 = {
        "key" : "key 1",
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
        "key": "key 2",
        "type": 2,
        "id": 234,
        "name": "proj2",
        "image": "another image.png",
        "tileserver_url": "http://tileserver.xyz",
        "input_geometries": "./data/builing_footprints_tanzania.geojson",
        "verificationCount": 3
    }

    imports = [import1, import2]
    return imports


class BaseProject(object):
    # add other methods that are common to all project types
    def __init__(self, info):
        # set basic project information
        self.name = info['name']
        self.image = info['image']
        self.id = info['id']
        self.verification_count = info['verificationCount']


    def import_project(self):

        print(vars(self))
        groups = self.create_groups()
        print('craeted %s groups' % len(groups))
        self.upload_groups_firebase(firebase, groups)
        self.upload_project_mysql(mysqlDB)
        self.upload_project_firebase(firebase)
        self.set_import_complete(firebase)


    def upload_groups_firebase(self, firebase, groups):
        print("uploaded %s groups to firebase." % len(groups))


    def upload_project_firebase(self, firebase):
        print("uploaded projet to firebase.")


    def upload_project_mysql(self, mysqlDB):
        print("uploaded projet to firebase.")


    def set_import_complete(self, firebase):
        print("set import complete in firebase")


class BaseGroup(object):
    def __init__(self, project, group_id):
        # set basic group information
        self.project_id = project.id
        self.id = group_id
        self.neededCount = project.verification_count
        self.completedCount = 0
        self.users = []


    def print_group_info(self):
        attrs = vars(self)
        print(attrs)


class BaseTask(object):
    def __init__(self, group, task_id):
        # set basic group information
        self.project_id = group.project_id
        self.group_id = group.id
        self.type = group.type
        self.id = task_id


    def print_task_info(self):
        attrs = vars(self)
        print(attrs)

########################################################################################################################
# Build Area Projects


class BuildAreaProject(BaseProject):
    def __init__(self, info):
        # super() executes fine now
        super(BuildAreaProject, self).__init__(info)
        self.type = 1

        self.info = {
            "tileserver": info['tileserver'],
            "zoomlevel": info['zoomlevel'],
            "extent": info['extent']
        }

        try:
            self.info["custom_tileserver_url"] = info['custom_tileserver_url']
        except:
            self.info["custom_tileserver_url"] = None


    def create_groups(self):
        groups = {}
        for i in range(0,3):
            groups[i] = vars(BuildAreaGroup(self, i))

        return groups


class BuildAreaGroup(BaseGroup):
    def __init__(self, project, group_id):
        # super() executes fine now
        super(BuildAreaGroup, self).__init__(project, group_id)
        self.type = 1
        self.create_tasks()

    def create_tasks(self):
        tasks = {}
        for i in range(0,3):
            tasks[i] = vars(BuildAreaTask(self, i))
        self.tasks = tasks


class BuildAreaTask(BaseTask):
    def __init__(self, group, task_id):
        # super() executes fine now
        super(BuildAreaTask, self).__init__(group, task_id)
        self.type = 1
        self.url = "123.png"


########################################################################################################################
# Footprint Projects

class FootprintProject(BaseProject):
    def __init__(self, info):
        # super() executes fine now
        super(FootprintProject, self).__init__(info)
        self.type = 2

        self.info = {
            "tileserver_url": info['tileserver_url'],
            "input_geometries": info['input_geometries']
        }

    def create_groups(self):
        groups = {}
        # here we create the groups according to the workflow of the project type
        for i in range(0,3):
            groups[i] = vars(FootprintGroup(self, i))

        return groups


class FootprintGroup(BaseGroup):
    def __init__(self, project, group_id):
        # super() executes fine now
        super(FootprintGroup, self).__init__(project, group_id)
        self.type = 2
        self.create_tasks()

    def create_tasks(self):
        tasks = {}
        for i in range(0,3):
            tasks[i] = vars(FootprintTask(self, i))
        self.tasks = tasks


class FootprintTask(BaseTask):
    def __init__(self, group, task_id):
        # super() executes fine now
        super(FootprintTask, self).__init__(group, task_id)
        self.type = 2
        self.geometry = "some polygon"
########################################################################################################################
# Main


if __name__ == '__main__':
    imports = get_new_imports()

    firebase = 'firebase'
    mysqlDB = 'mysqlDB'

    for new_import in imports:

        # this will be the place, where we distinguish different project types
        if new_import['type'] == 1:
            proj = BuildAreaProject(new_import)
            print('there is an import of type 1')
        elif new_import['type'] == 2:
            proj = FootprintProject(new_import)
            print('there is an import of type 2')
        else:
            # if there is a project with unknown type, we will skip it
            continue

        proj.import_project()

