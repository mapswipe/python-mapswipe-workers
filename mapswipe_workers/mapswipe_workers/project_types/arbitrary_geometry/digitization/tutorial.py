from mapswipe_workers.project_types.arbitrary_geometry.tutorial import (
    ArbitraryGeometryTutorial,
)


class DigitizationTutorial(ArbitraryGeometryTutorial):
    """The subclass for an TMS Grid based Tutorial."""

    def save_tutorial(self):
        raise NotImplementedError("Currently Digitization has no Tutorial")

    def create_tutorial_groups(self):
        raise NotImplementedError("Currently Digitization has no Tutorial")

    def create_tutorial_tasks(self):
        raise NotImplementedError("Currently Digitization has no Tutorial")
