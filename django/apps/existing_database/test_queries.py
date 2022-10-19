import datetime

from apps.aggregated.management.commands.update_aggregated_data import (
    Command as AggregateCommand,
)
from apps.existing_database.factories import (
    GroupFactory,
    ProjectFactory,
    ResultFactory,
    TaskFactory,
    UserFactory,
    UserGroupFactory,
)
from django.utils import timezone
from mapswipe.tests import TestCase


class ExistingDatabaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now() - datetime.timedelta(days=1)
        cls.user = UserFactory.create()
        # Project, Group, Task
        cls.project = ProjectFactory.create()
        cls.groups = GroupFactory.create_batch(3, project=cls.project)
        cls.tasks = [
            task
            for group in cls.groups
            for task in TaskFactory.create_batch(3, group=group)
        ]
        cls.results = {
            value: [
                ResultFactory.create(
                    task=task,
                    user=cls.user,
                    timestamp=now,
                    start_time=now,
                    end_time=now,
                    result=value,
                )
                for task in tasks
            ]
            for value, tasks in [
                (0, cls.tasks[:10]),
                (1, cls.tasks[10:]),
            ]
        }
        # UserGroups
        (
            cls.user_group1,
            cls.user_group2,
            cls.user_group3,
        ) = UserGroupFactory.create_batch(3)
        AggregateCommand().run()

    def test_community_stats(self):
        query = """
            query MyQuery {
              communityStats {
                totalContributors
                totalSwipes
                totalUserGroups
              }
            }
        """

        resp = self.query_check(query)
        self.assertEqual(
            resp["data"]["communityStats"],
            dict(
                totalContributors=1,
                totalSwipes=9,
                totalUserGroups=0,
            ),
        )
