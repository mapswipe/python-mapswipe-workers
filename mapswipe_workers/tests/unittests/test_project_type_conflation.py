import os
import unittest

from mapswipe_workers.project_types import ConflationProject
from tests import fixtures


class TestCreateConflationProject(unittest.TestCase):
    def setUp(self) -> None:
        project_draft = fixtures.get_fixture(
            os.path.join(
                "projectDrafts",
                "conflation.json",
            )
        )
        project_draft["projectDraftId"] = "foo"
        self.project = ConflationProject(project_draft)

    def test_init(self):
        self.assertEqual(self.project.geometry["type"], "FeatureCollection")
        self.assertEqual(self.project.inputType, "aoi_file")


if __name__ == "__main__":
    unittest.main()
