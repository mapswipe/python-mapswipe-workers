import factory
from factory.django import DjangoModelFactory

from .models import (
    User,
    UserGroup,
    UserGroupUserMembership,
    Project,
    Group,
    Task,
    Result,
    UserGroupResult,
)


class UserFactory(DjangoModelFactory):
    user_id = factory.Sequence(lambda n: f"dummy-user-id-{n}")
    username = factory.Sequence(lambda n: f"dummy-username-{n}")

    class Meta:
        model = User


class ProjectFactory(DjangoModelFactory):
    project_id = factory.Sequence(lambda n: f"dummy-project-id-{n}")

    class Meta:
        model = Project


class GroupFactory(DjangoModelFactory):
    group_id = factory.Sequence(lambda n: f"dummy-project-task-group-{n}")

    class Meta:
        model = Group


class TaskFactory(DjangoModelFactory):
    task_id = factory.Sequence(lambda n: f"dummy-project-task-{n}")

    class Meta:
        model = Task

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "group" not in kwargs:
            raise Exception("Please define group")
        group = kwargs.pop("group")
        kwargs["project"] = group.project
        kwargs["group_id"] = group.group_id
        return super()._create(model_class, *args, **kwargs)


class ResultFactory(DjangoModelFactory):
    class Meta:
        model = Result

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "task" not in kwargs:
            raise Exception("Please define task")
        task = kwargs.pop("task")
        kwargs["project"] = task.project
        kwargs["group_id"] = task.group_id
        kwargs["task_id"] = task.task_id
        return super()._create(model_class, *args, **kwargs)


class UserGroupResultFactory(DjangoModelFactory):
    class Meta:
        model = UserGroupResult

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "group" not in kwargs:
            raise Exception("Please define group")
        group = kwargs.pop("group")
        kwargs["project"] = group.project
        kwargs["group_id"] = group.group_id
        return super()._create(model_class, *args, **kwargs)


class UserGroupFactory(DjangoModelFactory):
    user_group_id = factory.Sequence(lambda n: f"dummy-user-group-id-{n}")
    name = factory.Sequence(lambda n: f"UserGroup-{n}")
    description = factory.Faker("sentence", nb_words=20)

    class Meta:
        model = UserGroup


class UserGroupMembershipFactory(DjangoModelFactory):
    class Meta:
        model = UserGroupUserMembership
