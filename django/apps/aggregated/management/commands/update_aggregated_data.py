import datetime
import time

from apps.aggregated.models import (
    AggregatedTracking,
    AggregatedUserGroupStatData,
    AggregatedUserStatData,
)
from apps.existing_database.models import Result
from django.core.management.base import BaseCommand
from django.db import connection, models, transaction
from django.utils import timezone

UPDATE_USER_DATA_SQL = f"""
    INSERT INTO "{AggregatedUserStatData._meta.db_table}" (
        project_id,
        user_id,
        timestamp_date,
        total_time,
        task_count,
        area_swiped,
        swipes
    )
    (
        -- Retrieve used tasks
        WITH used_tasks as (
            SELECT
              project_id, group_id, task_id
            FROM results R
              INNER JOIN tasks T USING (project_id, group_id, task_id)
            WHERE
                R.timestamp >= %(from_date)s and R.timestamp < %(until_date)s
            GROUP BY project_id, group_id, task_id
        ),
        -- Calculated task area.
        task_data as (
          SELECT
              project_id,
              group_id,
              task_id,
              ST_Area(geom::geography(GEOMETRY,4326)) / 1000000 as area -- sqkm
          FROM used_tasks
              INNER JOIN tasks T USING (project_id, group_id, task_id)
        ),
        -- Aggregate data by group
        user_data as (
            SELECT
              R.project_id,
              R.group_id,
              R.user_id,
              MAX(R.timestamp::date) as timestamp_date,
              MIN(R.start_time) as start_time,
              MAX(R.end_time) as end_time,
              COUNT(DISTINCT R.task_id) as task_count,
              SUM(T.area) as area_swiped
            From results R
              INNER JOIN task_data T USING (project_id, group_id, task_id)
            WHERE
                R.timestamp >= %(from_date)s and R.timestamp < %(until_date)s
            GROUP BY R.project_id, R.group_id, R.user_id
        ),
        -- Aggregate group data
        user_agg_data as (
          SELECT
            project_id,
            user_id,
            timestamp_date,
            COALESCE(SUM(EXTRACT(EPOCH FROM (end_time - start_time))), 0) as total_time,
            COALESCE(SUM(task_count), 0) as task_count,
            COALESCE(SUM(area_swiped), 0) as area_swiped
          FROM user_data
          GROUP BY project_id, user_id, timestamp_date
        )
        -- Precalculate additional values here.
        SELECT
          user_agg_data.*,
          CASE
              WHEN P.project_type in (1, 4) THEN ROUND(task_count/6)
              ELSE task_count
          END as swipes
          FROM user_agg_data
              INNER JOIN projects P USING (project_id)
    )
    ON CONFLICT (project_id, user_id, timestamp_date)
    DO UPDATE SET
        total_time = EXCLUDED.total_time,
        task_count = EXCLUDED.task_count,
        area_swiped = EXCLUDED.area_swiped,
        swipes = EXCLUDED.swipes;
"""


UPDATE_USER_GROUP_SQL = f"""
    INSERT INTO "{AggregatedUserGroupStatData._meta.db_table}" (
        project_id,
        user_id,
        user_group_id,
        timestamp_date,
        total_time,
        task_count,
        area_swiped,
        swipes
    )
    (
        -- Retrieve used tasks
        WITH used_tasks as (
            SELECT
              project_id, group_id, task_id
            From results_user_groups ug
                INNER JOIN results R USING (project_id, group_id, user_id)
                INNER JOIN tasks T USING (project_id, group_id, task_id)
            WHERE
                R.timestamp >= %(from_date)s and R.timestamp < %(until_date)s
            GROUP BY project_id, group_id, task_id
        ),
        -- Calculated task area.
        task_data as (
          SELECT
              project_id,
              group_id,
              task_id,
              ST_Area(geom::geography(GEOMETRY,4326)) / 1000000 as area -- sqkm
          FROM used_tasks
              INNER JOIN tasks T USING (project_id, group_id, task_id)
        ),
        -- Aggregate data by group
        user_group_data as (
            SELECT
                ug.project_id,
                ug.group_id,
                ug.user_id,
                ug.user_group_id,
                MAX(R.timestamp::date) as timestamp_date,
                MIN(R.start_time) as start_time,
                MAX(R.end_time) as end_time,
                COUNT(DISTINCT R.task_id) as task_count,
                SUM(T.area) as area_swiped
            From results_user_groups ug
                INNER JOIN results R USING (project_id, group_id, user_id)
                INNER JOIN task_data T USING (task_id)
            WHERE
                R.timestamp >= %(from_date)s and R.timestamp < %(until_date)s
            GROUP BY ug.project_id, ug.group_id, ug.user_id, ug.user_group_id
        ),
        -- Aggregate group data
        user_group_agg_data as (
          SELECT
            project_id,
            user_id,
            user_group_id,
            timestamp_date,
            COALESCE(SUM(EXTRACT(EPOCH FROM (end_time - start_time))), 0) as total_time,
            COALESCE(SUM(task_count), 0) as task_count,
            COALESCE(SUM(area_swiped), 0) as area_swiped
          FROM user_group_data
          GROUP BY project_id, user_id, user_group_id, timestamp_date
        )
        -- Precalculate additional values here.
        SELECT
          user_group_agg_data.*,
          CASE
              WHEN P.project_type in (1, 4) THEN ROUND(task_count/6)
              ELSE task_count
          END as swipes
          FROM user_group_agg_data
              INNER JOIN projects P USING (project_id)
    )
    ON CONFLICT (project_id, user_id, user_group_id, timestamp_date)
    DO UPDATE SET
        total_time = EXCLUDED.total_time,
        task_count = EXCLUDED.task_count,
        area_swiped = EXCLUDED.area_swiped,
        swipes = EXCLUDED.swipes;
"""


INTERVAL_RANGE_DAYS = 30


class Command(BaseCommand):
    def _track(self, tracker_type, label, sql):
        tracker, _ = AggregatedTracking.objects.get_or_create(type=tracker_type)
        now = timezone.now().date()
        # Fallback: For now only update from 1 day before instead of whole data
        # which is quite big.
        from_date = tracker.value
        if tracker.value is not None:
            from_date = datetime.datetime.strptime(tracker.value, "%Y-%m-%d").date()
        else:
            self.stdout.write(f"{label.title()} Last tracker data not found.")
            timestamp_min = Result.objects.aggregate(
                timestamp_min=models.Min("timestamp")
            )["timestamp_min"]
            if timestamp_min:
                self.stdout.write(f"Using min timestamp from database {timestamp_min}")
                from_date = timestamp_min.date()
            else:
                self.stdout.write("Nothing found from database.")
                from_date = now
        while True:
            until_date = min(
                now,
                from_date + datetime.timedelta(days=INTERVAL_RANGE_DAYS),
            )
            if from_date >= until_date:
                self.stdout.write(f"{label.title()} Nothing to do here.....")
                break
            params = dict(
                from_date=from_date.strftime("%Y-%m-%d"),
                until_date=until_date.strftime("%Y-%m-%d"),
            )
            start_time = time.time()
            self.stdout.write(f"Updating {label.title()} Data for date: {params}")
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfull. Runtime: {time.time() - start_time} seconds"
                    )
                )
                tracker.value = from_date = until_date
                self.stdout.write(f"Saving date {tracker.value} as last tracker")
                tracker.save()

    def run(self):
        self._track(
            AggregatedTracking.Type.AGGREGATED_USER_STAT_DATA_LATEST_DATE,
            "user",
            UPDATE_USER_DATA_SQL,
        )
        self._track(
            AggregatedTracking.Type.AGGREGATED_USER_GROUP_STAT_DATA_LATEST_DATE,
            "user_group",
            UPDATE_USER_GROUP_SQL,
        )

    def handle(self, **_):
        self.run()
