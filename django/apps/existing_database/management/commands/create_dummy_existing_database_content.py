import datetime

from apps.existing_database.factories import (
    GroupFactory,
    OrganizationFactory,
    ProjectFactory,
    ResultFactory,
    TaskFactory,
    UserFactory,
    UserGroupFactory,
    UserGroupMembershipFactory,
    UserGroupResultFactory,
)
from apps.existing_database.models import (
    Group,
    Project,
    Result,
    Task,
    User,
    UserGroup,
    UserGroupResult,
    UserGroupUserMembership,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_confirm = False

    def confirm(self, message):
        if self.skip_confirm:
            self.stdout.write(f"Skipping confirmation for <{message}>")
            return True
        confirm = input(f"{message}. Are you sure? [y/N]: ")
        if confirm != "y":
            self.stdout.write("Exiting....")
            return
        return True

    def clean(self):
        qs_set = []
        for model, id_field in [
            (UserGroupResult, "group_id"),
            (Result, "task_id"),
            (UserGroupUserMembership, "user__user_id"),
            (User, "user_id"),
            (UserGroup, "user_group_id"),
            (Task, "task_id"),
            (Group, "group_id"),
            (Project, "project_id"),
        ]:
            qs_set.append(model.objects.filter(**{f"{id_field}__startswith": "dummy"}))

        self.stdout.write("Deleting following objects")
        for qs in qs_set:
            self.stdout.write(f"- {qs.model.__name__}: {qs.count()}")
            for item in qs.all():
                self.stdout.write(f" - {item}")
        if not self.confirm(
            "This will add new data to and delete from the existing database."
        ):
            self.stdout.write("Exiting....")
            return
        for qs in qs_set:
            qs.delete()
        return True

    def handle(self, *args, **options):
        if not self.confirm(
            "This will add new data to and delete from the existing database"
        ):
            self.stdout.write("Exiting....")
            return

        if not self.clean():
            return

        user1, user2, user3 = UserFactory.create_batch(3)
        user_group1, user_group2, user_group3 = UserGroupFactory.create_batch(3)
        for user, is_active in [(user1, True), (user2, True), (user3, False)]:
            for user_group in [user_group1, user_group2, user_group3]:
                UserGroupMembershipFactory.create(
                    user=user,
                    user_group=user_group,
                    is_active=is_active,
                )
        (
            organization1,
            organization2,
            organization3,
            _,
        ) = OrganizationFactory.create_batch(4)
        project1 = ProjectFactory.create(organization=organization1)
        project2 = ProjectFactory.create(organization=organization2)
        project3 = ProjectFactory.create(organization=organization3)

        # Group
        p1_group1, p1_group2, _ = GroupFactory.create_batch(3, project=project1)
        p2_group1, p2_group2, _ = GroupFactory.create_batch(3, project=project2)
        p3_group1, p3_group2, _ = GroupFactory.create_batch(3, project=project3)
        # Task
        timestamp_now = datetime.datetime.now()
        TaskFactory.create_batch(3, group=p1_group1)
        TaskFactory.create_batch(3, group=p1_group2)
        TaskFactory.create_batch(3, group=p2_group1)
        TaskFactory.create_batch(3, group=p2_group2)
        TaskFactory.create_batch(3, group=p3_group1)
        TaskFactory.create_batch(3, group=p3_group2)

        start_time = datetime.datetime.now()
        for group, user, time_seconds, user_groups in [
            # Project 1
            (p1_group1, user1, 60, [user_group1, user_group2]),
            (p1_group2, user2, 120, [user_group2, user_group3]),
            # Project 2
            (p2_group1, user1, 330, [user_group1]),
            (p2_group1, user2, 10, [user_group2]),
            (p2_group2, user3, 50, [user_group1]),
            (p3_group1, user1, 330, [user_group1]),
            (p3_group2, user1, 330, [user_group1]),
        ]:
            end_time = start_time + datetime.timedelta(seconds=time_seconds)
            for task, timestamp in [
                (
                    Task.objects.filter(group_id=group.group_id)[0],
                    timestamp_now + datetime.timedelta(days=-19),
                ),
                (
                    Task.objects.filter(group_id=group.group_id)[1],
                    timestamp_now + datetime.timedelta(days=-12),
                ),
                (
                    Task.objects.filter(group_id=group.group_id)[2],
                    timestamp_now + datetime.timedelta(days=-14),
                ),
            ]:
                ResultFactory.create(
                    task=task,
                    user=user,
                    start_time=start_time,
                    end_time=end_time,
                    timestamp=timestamp,
                )
            for user_group in user_groups:
                UserGroupResultFactory.create(
                    group=group,
                    user=user,
                    user_group=user_group,
                )
