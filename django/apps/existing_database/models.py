from django.contrib.gis.db import models as gis_models
from django.db import models

from mapswipe.db import Model


class User(Model):
    user_id = models.CharField(primary_key=True, max_length=999)
    username = models.CharField(max_length=999, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return self.user_id


class UserGroup(Model):
    user_group_id = models.CharField(primary_key=True, max_length=999)
    name = models.CharField(max_length=999, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, models.DO_NOTHING, related_name='+')
    archived_at = models.DateTimeField(blank=True, null=True)
    archived_by = models.ForeignKey(User, models.DO_NOTHING, related_name='+')
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user_groups"

    def __str__(self):
        return self.user_group_id

    def user_memberships(self):
        return UserGroupUserMembership.objects.filter(
            user_group_id=self.user_group_id
        ).select_related("user")


class UserGroupUserMembership(Model):
    user_group = models.ForeignKey(UserGroup, models.DO_NOTHING, related_name='+')
    user = models.ForeignKey(User, models.DO_NOTHING, related_name='+')
    is_active = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "user_groups_user_memberships"
        unique_together = (("user_group", "user"),)

    def __str__(self):
        return f"UG:{self.user_group_id}-U:{self.user_id}"


class Project(Model):
    class ProjectType(models.IntegerChoices):
        BUILD_AREA = 1, "Build Area"
        FOOTPRINT = 2, "Footprint"
        CHANGE_DETECTION = 3, "Change Detection"
        COMPLETENESS = 4, "Completeness"

    project_id = models.CharField(primary_key=True, max_length=999)
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=999, blank=True, null=True)
    geom = gis_models.GeometryField(blank=True, null=True)
    image = models.CharField(max_length=999, blank=True, null=True)
    is_featured = models.BooleanField(blank=True, null=True)
    look_for = models.CharField(max_length=999, blank=True, null=True)
    name = models.CharField(max_length=999, blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)
    project_details = models.CharField(max_length=999, blank=True, null=True)
    project_type = models.IntegerField(
        choices=ProjectType.choices, blank=True, null=True)
    required_results = models.IntegerField(blank=True, null=True)
    result_count = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=999, blank=True, null=True)
    verification_number = models.IntegerField(blank=True, null=True)
    # Database uses JSON instead of JSONB (not supported by django)
    project_type_specifics = models.TextField(blank=True, null=True)
    organization_name = models.CharField(max_length=1000, null=True, blank=True)

    objects: models.Manager

    class Meta:
        managed = False
        db_table = "projects"

    def __str__(self):
        return self.project_id


class Group(Model):
    # NOTE: Primary Key: project_id, group_id
    group_id = models.CharField(primary_key=True, max_length=999)
    project = models.ForeignKey("Project", models.DO_NOTHING, related_name='+')
    number_of_tasks = models.IntegerField(blank=True, null=True)
    finished_count = models.IntegerField(blank=True, null=True)
    required_count = models.IntegerField(blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)
    # Database uses JSON instead of JSONB (not supported by django)
    project_type_specifics = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "groups"
        unique_together = (("project", "group_id"),)

    def __str__(self):
        return f"P:{self.project_id}-G:{self.group_id}"


class Task(Model):
    # NOTE: Primary Key: project_id, group_id, tasks_id
    project = models.ForeignKey(Project, models.DO_NOTHING, related_name='+')
    group_id = models.CharField(max_length=999)
    task_id = models.CharField(max_length=999)
    geom = gis_models.MultiPolygonField(blank=True, null=True)
    # Database uses JSON instead of JSONB (not supported by django)
    project_type_specifics = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "tasks"
        unique_together = (("project", "group_id", "task_id"),)

    @property
    def group(self):
        return Group.objects.filter(
            project=self.project, group_id=self.group_id
        ).first()

    def __str__(self):
        return f"P:{self.project_id}-G:{self.group_id}-T:{self.task_id}"


class Result(Model):
    # NOTE: Primary Key: project_id, group_id, tasks_id, user_id
    project = models.ForeignKey(Project, models.DO_NOTHING, related_name='+')
    group_id = models.CharField(max_length=999)
    task_id = models.CharField(max_length=999)
    user = models.ForeignKey(User, models.DO_NOTHING, related_name='+')
    timestamp = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "results"
        unique_together = (("project", "group_id", "task_id", "user"),)

    def __str__(self):
        return (
            f"P:{self.project_id}-G:{self.group_id}-T:{self.task_id}-U:{self.user_id}"
        )

    @property
    def group(self):
        return Group.objects.filter(
            project=self.project,
            group_id=self.group_id,
        ).first()

    @property
    def task(self):
        return Task.objects.filter(
            project=self.project,
            group_id=self.group_id,
            task_id=self.task_id,
        ).first()


class UserGroupResult(Model):
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='+')
    group_id = models.CharField(max_length=999)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    user_group = models.ForeignKey(
        UserGroup, on_delete=models.DO_NOTHING, related_name='+'
    )

    class Meta:
        managed = False
        db_table = "results_user_groups"
        unique_together = (("project", "group_id", "user_id", "user_group"),)

    def __str__(self):
        return (
            f"P:{self.project_id}-G:{self.group_id}"
            "-UG:{self.user_group_id}-U:{self.user_id}"
        )

    @property
    def group(self):
        return Group.objects.filter(
            project=self.project,
            group_id=self.group_id,
        ).first()
