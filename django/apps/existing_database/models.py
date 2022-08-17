from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.contrib.postgres.fields import ArrayField


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=-1)
    username = models.CharField(max_length=-1, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"
        app_label = settings.MAPSWIPE_EXISTING_DB

    def __str__(self):
        return self.user_id


class UserGroup(models.Model):
    user_group_id = models.CharField(primary_key=True, max_length=-1)
    name = models.CharField(max_length=-1, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, models.DO_NOTHING)
    archived_at = models.DateTimeField(blank=True, null=True)
    archived_by = models.ForeignKey(User, models.DO_NOTHING)
    is_archived = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user_groups"
        app_label = settings.MAPSWIPE_EXISTING_DB

    def __str__(self):
        return self.user_group_id

    def user_memberships(self):
        return UserGroupUserMembership.objects.filter(
            user_group_id=self.user_group_id
        ).select_related("user")


class UserGroupUserMembership(models.Model):
    user_group = models.ForeignKey(UserGroup, models.DO_NOTHING, primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, primary_key=True)
    is_active = models.BooleanField(null=True, blank=True)
    left_at = ArrayField(models.DateTimeField(blank=True, null=True), default=dict)
    joined_at = ArrayField(models.DateTimeField(blank=True, null=True), default=dict)

    class Meta:
        managed = False
        db_table = "user_groups_user_memberships"
        unique_together = (("user_group", "user"),)
        app_label = settings.MAPSWIPE_EXISTING_DB

    def __str__(self):
        return f"UG:{self.user_group_id}-U:{self.user_id}"


class Organization(models.Model):
    organization_id = models.CharField(primary_key=True, max_length=-1)

    class Meta:
        managed = False
        db_table = "organizations"
        app_label = settings.MAPSWIPE_EXISTING_DB

    def __str__(self):
        return self.organization_id


class Project(models.Model):
    project_id = models.CharField(primary_key=True, max_length=-1)
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=-1, blank=True, null=True)
    geom = gis_models.GeometryField(blank=True, null=True)
    image = models.CharField(max_length=-1, blank=True, null=True)
    is_featured = models.BooleanField(blank=True, null=True)
    look_for = models.CharField(max_length=-1, blank=True, null=True)
    name = models.CharField(max_length=-1, blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)
    project_details = models.CharField(max_length=-1, blank=True, null=True)
    project_type = models.IntegerField(blank=True, null=True)
    required_results = models.IntegerField(blank=True, null=True)
    result_count = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=-1, blank=True, null=True)
    verification_number = models.IntegerField(blank=True, null=True)
    # Database uses JSON instead of JSONB (not supported by django)
    project_type_specifics = models.TextField(blank=True, null=True)
    organization_name = models.CharField(max_length=-1, null=True, blank=True)
    # organization = models.ForeignKey(Organization, models.DO_NOTHING, primary_key=True)

    class Meta:
        managed = False
        db_table = "projects"
        unique_together = (("project_id", "organization"),)
        app_label = settings.MAPSWIPE_EXISTING_DB

    def __str__(self):
        return self.project_id


class Group(models.Model):
    # NOTE: Primary Key: project_id, group_id
    project = models.ForeignKey("Project", models.DO_NOTHING, primary_key=True)
    group_id = models.CharField(max_length=-1)
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
        app_label = settings.MAPSWIPE_EXISTING_DB

    def __str__(self):
        return f"P:{self.project_id}-G:{self.group_id}"


class Task(models.Model):
    # NOTE: Primary Key: project_id, group_id, tasks_id
    project = models.ForeignKey(Project, models.DO_NOTHING, primary_key=True)
    group_id = models.CharField(max_length=-1, primary_key=True)
    task_id = models.CharField(max_length=-1, primary_key=True)
    geom = gis_models.MultiPolygonField(blank=True, null=True)
    # Database uses JSON instead of JSONB (not supported by django)
    project_type_specifics = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "tasks"
        unique_together = (("project", "group_id", "task_id"),)
        app_label = settings.MAPSWIPE_EXISTING_DB

    @property
    def group(self):
        return Group.objects.filter(
            project=self.project, group_id=self.group_id
        ).first()

    def __str__(self):
        return f"P:{self.project_id}-G:{self.group_id}-T:{self.task_id}"


class Result(models.Model):
    # NOTE: Primary Key: project_id, group_id, tasks_id, user_id
    project = models.ForeignKey(Project, models.DO_NOTHING, primary_key=True)
    group_id = models.CharField(max_length=-1, primary_key=True)
    task_id = models.CharField(max_length=-1, primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, primary_key=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "results"
        unique_together = (("project", "group_id", "task_id", "user"),)
        app_label = settings.MAPSWIPE_EXISTING_DB

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


class UserGroupResult(models.Model):
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, primary_key=True)
    group_id = models.CharField(max_length=-1, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, primary_key=True)
    user_group = models.ForeignKey(
        UserGroup, on_delete=models.DO_NOTHING, primary_key=True
    )

    class Meta:
        managed = False
        db_table = "results_user_groups"
        unique_together = (("project", "group_id", "user_id", "user_group"),)
        app_label = settings.MAPSWIPE_EXISTING_DB

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
