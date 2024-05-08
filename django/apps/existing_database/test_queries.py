import datetime

from apps.aggregated.factories import AggregatedUserGroupStatDataFactory
from apps.aggregated.management.commands.update_aggregated_data import (
    Command as AggregateCommand,
)
from apps.existing_database.factories import (
    GroupFactory,
    MappingSessionFactory,
    MappingSessionResultFactory,
    MappingSessionUserGroupFactory,
    ProjectFactory,
    TaskFactory,
    UserFactory,
    UserGroupFactory,
    UserGroupMembershipFactory,
)
from apps.existing_database.models import Project, UserGroup
from django.utils import timezone
from mapswipe.tests import TestCase


class ExistingDatabaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now() - datetime.timedelta(days=1)
        cls.user = UserFactory.create()
        # Project, Group, Task
        cls.project = ProjectFactory.create()
        cls.groups = GroupFactory.create_batch(4, project=cls.project)
        cls.tasks = [
            task
            for group in cls.groups
            for task in TaskFactory.create_batch(4, group=group)
        ]
        cls.mapping_sessions = {
            group.group_id: MappingSessionFactory(
                project_id=group.project_id,
                group_id=group.group_id,
                user=cls.user,
                start_time=now,
                end_time=now,
                items_count=2,
            )
            for group in cls.groups
        }
        cls.results = {
            value: [
                MappingSessionResultFactory.create(
                    mapping_session=cls.mapping_sessions.get(task.group_id),
                    task_id=task.task_id,
                    result=value,
                )
                for task in tasks
            ]
            for value, tasks in [
                (0, cls.tasks[:8]),
                (1, cls.tasks[8:]),
            ]
        }
        cls.user_groups = UserGroupFactory.create_batch(4)
        cls.user_group_results = [
            MappingSessionUserGroupFactory(
                mapping_session=result.mapping_session,
                user_group=user_group,
            )
            for results_set, user_groups in [
                (cls.results[0], cls.user_groups[:2]),
                (cls.results[1], cls.user_groups[3:]),
            ]
            for result in results_set
            for user_group in user_groups
        ]
        AggregateCommand().run()

    def test_community_stats(self):
        query = """
            query MyQuery {
              communityStats {
                totalContributors
                totalSwipes
                totalUserGroups
              }
              communityStatsLatest {
                totalContributors
                totalSwipes
                totalUserGroups
              }
            }
        """

        resp = self.query_check(query)
        assert resp["data"] == dict(
            communityStats=dict(
                totalContributors=1,
                totalSwipes=8,
                totalUserGroups=3,
            ),
            communityStatsLatest=dict(
                totalContributors=1,
                totalSwipes=8,
                totalUserGroups=3,
            ),
        )

    def test_user_group_aggregated_calc(self):
        query = """
            query MyQuery($userGroupId: ID!) {
              userGroupStats(userGroupId: $userGroupId) {
                stats {
                  totalAreaSwiped
                  totalContributors
                  totalMappingProjects
                  totalOrganization
                  totalSwipeTime
                  totalSwipes
                }
              }
            }
        """
        with_data = dict(
            totalAreaSwiped=0,
            totalContributors=1,
            totalMappingProjects=1,
            totalOrganization=0,
            totalSwipeTime=0,
            totalSwipes=16,
        )
        without_data = dict(
            totalAreaSwiped=0,
            totalContributors=0,
            totalMappingProjects=0,
            totalOrganization=0,
            totalSwipeTime=0,
            totalSwipes=0,
        )
        resp_collection = {}
        for user_group in self.user_groups:
            resp = self.query_check(
                query,
                variables=dict(
                    userGroupId=user_group.user_group_id,
                ),
            )
            resp_collection[user_group.user_group_id] = resp["data"]["userGroupStats"][
                "stats"
            ]
        assert resp_collection == {
            user_group.user_group_id: (without_data if index == 2 else with_data)
            for index, user_group in enumerate(self.user_groups)
        }

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
                  offset
                  limit
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
        project = ProjectFactory.create(project_type=Project.Type.BUILD_AREA)
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
                        "totalSwipes": 12,
                        "userId": users[0].user_id,
                        "username": users[0].username,
                    },
                    {
                        "isActive": True,
                        "totalMappingProjects": 1,
                        "totalSwipeTime": 20,
                        "totalSwipes": 24,
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
                        "totalSwipes": 36,
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
                            "offset": offset,
                            "limit": 2,
                            "items": expected_memberships,
                        },
                    },
                },
            }

    def test_user_groups_query(self):
        query = """
            query MyQuery($pagination: OffsetPaginationInput!) {
              userGroups(pagination: $pagination, order: {userGroupId: ASC}) {
                count
                offset
                limit
                items {
                    name
                    createdAt
                    archivedAt
                    isArchived
                  }
              }
            }
        """
        existing_user_groups_count = UserGroup.objects.count()
        # UserGroup with None name should not be filtered out
        UserGroupFactory.create_batch(3, name=None)

        offset = 0
        resp = self.query_check(
            query,
            variables=dict(
                pagination=dict(
                    limit=2,
                    offset=offset,
                ),
            ),
        )
        assert resp == {
            "data": {
                "userGroups": {
                    "count": existing_user_groups_count,
                    "limit": 2,
                    "offset": offset,
                    "items": [
                        {
                            "archivedAt": user_group.archived_at,
                            "createdAt": user_group.created_at,
                            "isArchived": user_group.is_archived,
                            "name": user_group.name,
                        }
                        for user_group in self.user_groups[:2]
                    ],
                },
            },
        }

    def test_user_query(self):
        # TODO:
        query = """
            query MyQuery($userId: ID!, $pagination: OffsetPaginationInput!) {
              user(pk: $userId) {
                id
                userId
                username
                userInUserGroups(pagination: $pagination) {
                  count
                  offset
                  limit
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
            # Additional users
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
                        "id": user.user_id,
                        "userId": user.user_id,
                        "username": user.username,
                        "userInUserGroups": {
                            "count": 3,
                            "offset": offset,
                            "limit": 2,
                            "items": expected_memberships,
                        },
                    },
                },
            }
