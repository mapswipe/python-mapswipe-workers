from django.db import models
from django.contrib.gis.db import models as gis_models
from django.conf import settings


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=-1)
    username = models.CharField(max_length=-1, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
        app_label = settings.MAPSWIPE_EXISTING_DB


class UserGroup(models.Model):
    user_group_id = models.CharField(primary_key=True, max_length=-1)
    name = models.CharField(max_length=-1)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_groups'
        app_label = settings.MAPSWIPE_EXISTING_DB


class UserGroupUserMembership(models.Model):
    user_group = models.ForeignKey(UserGroup, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_groups_user_memberships'
        unique_together = (('user_group', 'user'),)
        app_label = settings.MAPSWIPE_EXISTING_DB


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

    class Meta:
        managed = False
        db_table = 'projects'
        app_label = settings.MAPSWIPE_EXISTING_DB


class Group(models.Model):
    # NOTE: Primary Key: project_id, group_id
    project = models.ForeignKey('Project', models.DO_NOTHING, primary_key=True)
    group_id = models.CharField(max_length=-1)
    number_of_tasks = models.IntegerField(blank=True, null=True)
    finished_count = models.IntegerField(blank=True, null=True)
    required_count = models.IntegerField(blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)
    # Database uses JSON instead of JSONB (not supported by django)
    project_type_specifics = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'groups'
        unique_together = (('project', 'group_id'),)
        app_label = settings.MAPSWIPE_EXISTING_DB


# Multiple columns primary keys objects

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
        db_table = 'tasks'
        unique_together = (('project', 'group_id', 'task_id'),)
        app_label = settings.MAPSWIPE_EXISTING_DB

    @property
    def group(self):
        return Group.objects\
            .filter(project=self.project, group_id=self.group_id)\
            .first()


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
        db_table = 'results'
        unique_together = (('project', 'group_id', 'task_id', 'user'),)
        app_label = settings.MAPSWIPE_EXISTING_DB

    @property
    def group(self):
        return Group.objects\
            .filter(
                project=self.project,
                group_id=self.group_id,
            )\
            .first()

    @property
    def task(self):
        return Task.objects\
            .filter(
                project=self.project,
                group_id=self.group_id,
                task_id=self.task_id,
            )\
            .first()


class UserGroupResult(models.Model):
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, primary_key=True)
    group_id = models.CharField(max_length=-1, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, primary_key=True)
    user_group = models.ForeignKey(
        UserGroup, on_delete=models.DO_NOTHING, primary_key=True)

    class Meta:
        managed = False
        db_table = 'results_user_groups'
        unique_together = (('project', 'group_id', 'user_id', 'user_group'),)
        app_label = settings.MAPSWIPE_EXISTING_DB

    @property
    def group(self):
        return Group.objects\
            .filter(
                project=self.project,
                group_id=self.group_id,
            )\
            .first()