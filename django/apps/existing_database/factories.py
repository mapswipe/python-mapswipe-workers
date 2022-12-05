import factory
import factory.fuzzy
from factory.django import DjangoModelFactory
from mapswipe.utils import raise_if_field_not_found

from .models import (
    Group,
    MappingSession,
    MappingSessionResult,
    MappingSessionUserGroup,
    Project,
    Task,
    User,
    UserGroup,
    UserGroupUserMembership,
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
        raise_if_field_not_found(kwargs, ["group"])
        group = kwargs.pop("group")
        kwargs["project"] = group.project
        kwargs["group_id"] = group.group_id
        return super()._create(model_class, *args, **kwargs)


class MappingSessionFactory(DjangoModelFactory):
    class Meta:
        model = MappingSession


class MappingSessionResultFactory(DjangoModelFactory):
    class Meta:
        model = MappingSessionResult


class MappingSessionUserGroupFactory(DjangoModelFactory):
    class Meta:
        model = MappingSessionUserGroup

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return super()._create(model_class, *args, **kwargs)


class UserGroupFactory(DjangoModelFactory):
    user_group_id = factory.Sequence(lambda n: f"dummy-user-group-id-{n}")
    name = factory.Sequence(lambda n: f"UserGroup-{n}")
    description = factory.Faker("sentence", nb_words=20)
    archived_by_id = factory.SubFactory(UserFactory)
    created_by_id = factory.SubFactory(UserFactory)

    class Meta:
        model = UserGroup


class UserGroupMembershipFactory(DjangoModelFactory):
    class Meta:
        model = UserGroupUserMembership
