from django.db import models
from django.contrib.postgres.fields import ArrayField

from mapswipe.db import Model
from apps.existing_database.models import Project, User, UserGroup


class AggregatedTracking(Model):
    class Type(models.IntegerChoices):
        AGGREGATED_USER_STAT_DATA_LATEST_DATE = 0
        AGGREGATED_USER_GROUP_STAT_DATA_LATEST_DATE = 1

    type = models.IntegerField(choices=Type.choices)
    updated_at = models.DateTimeField(auto_now=True)
    value = models.CharField(max_length=225)


class AggregatedUserStatData(Model):
    # Ref Fields
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='+')
    timestamp_date = models.DateField()
    # Aggregated Fields
    total_time = models.DurationField()  # seconds
    task_count = models.FloatField()  # Number of tasks
    swipes = models.FloatField()  # Number of swipes
    area_swiped = models.FloatField()
    user_group_ids = ArrayField(models.CharField(max_length=255))

    class Meta:
        unique_together = (
            'project',
            'user',
            'timestamp_date',
        )


class AggregatedUserGroupStatData(Model):
    # Ref Fields
    user_group = models.ForeignKey(
        UserGroup, on_delete=models.DO_NOTHING, related_name='+')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='+')
    timestamp_date = models.DateField()
    # Aggregated Fields
    total_time = models.DurationField()  # seconds
    task_count = models.FloatField()  # Number of tasks
    swipes = models.FloatField()  # Number of swipes
    area_swiped = models.FloatField()
    total_user_groups = models.FloatField()

    class Meta:
        unique_together = (
            'project',
            'user',
            'user_group',
            'timestamp_date',
        )
