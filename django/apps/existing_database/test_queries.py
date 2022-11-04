import datetime

from apps.aggregated.factories import AggregatedUserGroupStatDataFactory
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
    UserGroupMembershipFactory,
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

    def test_user_group_query(self):
        query = """
            query MyQuery($userGroupId: ID!, $pagination: OffsetPaginationInput!) {
              userGroup(pk: $userGroupId) {
                name
                createdAt
                archivedAt
                isArchived
                userMemberships(pagination: $pagination) {
                  count
                  items {
                    userId
                    username
                    isActive
                    totalMappingProjects
                    totalSwipeTime
                    totalSwipes
                  }
                }
              }
            }
        """
        user_group = UserGroupFactory.create()
        project = ProjectFactory.create()
        users = UserFactory.create_batch(4)
        # Create some memberships
        for index, user in enumerate(users, start=1):
            if index <= 3:
                UserGroupMembershipFactory.create(user_group=user_group, user=user)
            AggregatedUserGroupStatDataFactory.create(
                project=project,
                user=user,
                user_group=user_group,
                timestamp_date="2020-01-01",
                total_time=10 * index,
                task_count=(10 + 1) * index,
                swipes=(10 + 2) * index,
                area_swiped=(10 + 3) * index,
            )

        for offset, expected_memberships in [
            (
                0,
                [
                    {
                        "isActive": True,
                        "totalMappingProjects": 1,
                        "totalSwipeTime": 10,
                        "totalSwipes": 11,
                        "userId": users[0].user_id,
                        "username": users[0].username,
                    },
                    {
                        "isActive": True,
                        "totalMappingProjects": 1,
                        "totalSwipeTime": 20,
                        "totalSwipes": 22,
                        "userId": users[1].user_id,
                        "username": users[1].username,
                    },
                ],
            ),
            (
                2,
                [
                    {
                        "isActive": True,
                        "totalMappingProjects": 1,
                        "totalSwipeTime": 30,
                        "totalSwipes": 33,
                        "userId": users[2].user_id,
                        "username": users[2].username,
                    },
                ],
            ),
        ]:
            resp = self.query_check(
                query,
                variables=dict(
                    userGroupId=user_group.user_group_id,
                    pagination=dict(
                        limit=2,
                        offset=offset,
                    ),
                ),
            )
            assert resp == {
                "data": {
                    "userGroup": {
                        "archivedAt": user_group.archived_at,
                        "createdAt": user_group.created_at,
                        "isArchived": user_group.is_archived,
                        "name": user_group.name,
                        "userMemberships": {
                            "count": 3,
                            "items": expected_memberships,
                        },
                    },
                },
            }

    def test_user_query(self):
        # TODO:
        query = """
            query MyQuery($userId: ID!, $pagination: OffsetPaginationInput!) {
              user(pk: $userId) {
                userId
                username
                userInUserGroups(pagination: $pagination) {
                  count
                  items {
                    userGroupId
                    userGroupName
                    membersCount
                  }
                }
              }
            }
        """
        user = UserFactory.create()
        additional_users = UserFactory.create_batch(3)
        project = ProjectFactory.create()
        user_groups = UserGroupFactory.create_batch(4)
        # Create some memberships
        for index, user_group in enumerate(user_groups, start=1):
            if index <= 3:
                UserGroupMembershipFactory.create(
                    user_group=user_group,
                    user=user,
                )
            # Additinal users
            for additional_user in additional_users[:index]:
                UserGroupMembershipFactory.create(
                    user_group=user_group, user=additional_user
                )
            AggregatedUserGroupStatDataFactory.create(
                project=project,
                user=user,
                user_group=user_group,
                timestamp_date="2020-01-01",
                total_time=10 * index,
                task_count=(10 + 1) * index,
                swipes=(10 + 2) * index,
                area_swiped=(10 + 3) * index,
            )

        for offset, expected_memberships in [
            (
                0,
                [
                    {
                        "userGroupId": user_groups[0].user_group_id,
                        "userGroupName": user_groups[0].name,
                        "membersCount": 2,
                    },
                    {
                        "userGroupId": user_groups[1].user_group_id,
                        "userGroupName": user_groups[1].name,
                        "membersCount": 3,
                    },
                ],
            ),
            (
                2,
                [
                    {
                        "userGroupId": user_groups[2].user_group_id,
                        "userGroupName": user_groups[2].name,
                        "membersCount": 4,
                    },
                ],
            ),
        ]:
            resp = self.query_check(
                query,
                variables=dict(
                    userId=user.user_id,
                    pagination=dict(
                        limit=2,
                        offset=offset,
                    ),
                ),
            )
            assert resp == {
                "data": {
                    "user": {
                        "userId": user.user_id,
                        "username": user.username,
                        "userInUserGroups": {
                            "count": 3,
                            "items": expected_memberships,
                        },
                    },
                },
            }
