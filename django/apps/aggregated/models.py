from apps.existing_database.models import Project, User, UserGroup
from django.db import models
from mapswipe.db import Model


class AggregatedTracking(Model):
    class Type(models.IntegerChoices):
        AGGREGATED_USER_STAT_DATA_LATEST_DATE = 0
        AGGREGATED_USER_GROUP_STAT_DATA_LATEST_DATE = 1

    """
    value: represents the date before which data is copied to aggregated tables.
    """
    type = models.IntegerField(choices=Type.choices, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    value = models.CharField(max_length=225, null=True)


class AggregatedUserStatData(Model):
    # Ref Fields
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="+")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    timestamp_date = models.DateField()
    # Aggregated Fields
    total_time = models.IntegerField()  # seconds
    task_count = models.IntegerField()  # Number of tasks
    swipes = models.IntegerField()  # Number of swipes
    area_swiped = models.FloatField()  # sqkm

    class Meta:
        unique_together = (
            "project",
            "user",
            "timestamp_date",
        )


class AggregatedUserGroupStatData(Model):
    # Ref Fields
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="+")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    user_group = models.ForeignKey(
        UserGroup, on_delete=models.CASCADE, related_name="+"
    )
    timestamp_date = models.DateField()
    # Aggregated Fields
    total_time = models.IntegerField()  # seconds
    task_count = models.FloatField()  # Number of tasks
    swipes = models.FloatField()  # Number of swipes
    area_swiped = models.FloatField()

    class Meta:
        unique_together = (
            "project",
            "user",
            "user_group",
            "timestamp_date",
        )
