from mapswipe_workers.project_types.tutorial import BaseTutorial


class StreetTutorial(BaseTutorial):
    """The subclass for an TMS Grid based Tutorial."""

    def save_tutorial(self):
        raise NotImplementedError("Currently Street has no Tutorial")

    def create_tutorial_groups(self):
        raise NotImplementedError("Currently Street has no Tutorial")

    def create_tutorial_tasks(self):
        raise NotImplementedError("Currently Street has no Tutorial")
