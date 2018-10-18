

class BaseProject():
    subclasses = {}

    # add other methods that are common to all project types

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.project_type] = cls


class BuildAreaProject(BaseProject):
    project_type = 1

    @classmethod
    def do_something(cls, params):
        # being a classmethod, you won't be able to access object ('self.xxx') attributes here
        # but you can factor your code nicely, without having to write tons of "if type == 1"
        print('hello from BuildAreaProject')


class FootprintProject(BaseProject):
    project_type = 2

    @classmethod
    def do_something(cls, params):
        print('hello from FootprintProject')


if __name__ == '__main__':
    proj1 = BuildAreaProject()
    proj2 = FootprintProject()

    proj1.do_something('')
    proj2.do_something('')

    print('magic now!')
    projlist = []
    # you can create new projects based on the type you find in the db:
    for idx in [1, 2]:
        projlist.append(BaseProject.subclasses[idx]())

    # with this, you should be able to operate on your projects without worrying which type they are
    for p in projlist:
        # two ways to access your methods
        BaseProject.subclasses[p.project_type].do_something('')
        p.do_something('')
