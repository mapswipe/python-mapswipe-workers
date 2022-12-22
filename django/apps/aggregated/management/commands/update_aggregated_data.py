import datetime
import time

from apps.aggregated.models import (
    AggregatedTracking,
    AggregatedUserGroupStatData,
    AggregatedUserStatData,
)
from apps.existing_database.models import MappingSession, Project
from django.core.management.base import BaseCommand
from django.db import connection, models, transaction
from django.utils import timezone

# Factor calculated by @Hagellach37
# For defining the threshold for outliers using `95_percent`
# Used by TASK_GROUP_METADATA_QUERY
# |project_type|median|95_percent|avg|
# |------------|------|----------|---|
# |1|00:00:00.208768|00:00:01.398161|00:00:28.951521|
# |2|00:00:01.330297|00:00:06.076814|00:00:03.481192|
# |3|00:00:02.092967|00:00:11.271081|00:00:06.045881|
TASK_GROUP_METADATA_QUERY = f"""
          SELECT
              project_id,
              group_id,
              SUM(
                ST_Area(geom::geography(GEOMETRY,4326)) / 1000000
              ) as total_task_group_area, -- sqkm
              (
                CASE
                  -- Using 95_percent value of existing data for each project_type
                  WHEN UG.project_type = {Project.Type.BUILD_AREA.value} THEN 1.4
                  WHEN UG.project_type = {Project.Type.COMPLETENESS.value} THEN 1.4
                  WHEN UG.project_type = {Project.Type.CHANGE_DETECTION.value} THEN 11.2
                  -- FOOTPRINT: Not calculated right now
                  WHEN UG.project_type = {Project.Type.FOOTPRINT.value} THEN 6.1
                  ELSE 1
                END
              ) * COUNT(*) as time_spent_max_allowed
          FROM tasks T
              INNER JOIN used_task_groups UG USING (project_id, group_id)
          GROUP BY project_id, project_type, group_id
"""


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
        -- Retrieve used task groups
        WITH used_task_groups as (
            SELECT
              MS.project_id,
              P.project_type,
              MS.group_id
            FROM mapping_sessions MS
                INNER JOIN projects P USING (project_id)
            WHERE
                -- Skip for footprint type missions
                P.project_type != {Project.Type.FOOTPRINT.value}
                AND MS.start_time >= %(from_date)s
                AND MS.start_time < %(until_date)s
            GROUP BY project_id, project_type, group_id -- To get unique
        ),
        -- Calculated area by task_groups
        task_group_metadata as ({TASK_GROUP_METADATA_QUERY}),
        -- Aggregate data by user
        user_data as (
            SELECT
              MS.project_id,
              MS.group_id,
              MS.user_id,
              MS.start_time::date as timestamp_date,
              LEAST(
                  EXTRACT(EPOCH FROM (MS.end_time - MS.start_time)),
                  TG.time_spent_max_allowed
              ) as time_spent_sec,
              MS.items_count as task_count,
              Coalesce(TG.total_task_group_area, 0) as area_swiped
            FROM mapping_sessions MS
                LEFT JOIN task_group_metadata TG USING (project_id, group_id)
            WHERE
                MS.start_time >= %(from_date)s
                AND MS.start_time < %(until_date)s
        ),
        -- Additional aggregate by timestamp_date
        user_agg_data as (
          SELECT
            project_id,
            user_id,
            timestamp_date,
            COALESCE(SUM(time_spent_sec), 0) as total_time,
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
        -- Retrieve used task groups
        WITH used_task_groups as (
            SELECT
              MS.project_id,
              P.project_type,
              MS.group_id
            FROM mapping_sessions_user_groups MSUR
                INNER JOIN mapping_sessions MS USING (mapping_session_id)
                INNER JOIN projects P USING (project_id)
            WHERE
                -- Skip for footprint type missions
                P.project_type != {Project.Type.FOOTPRINT.value}
                AND MS.start_time >= %(from_date)s
                AND MS.start_time < %(until_date)s
            GROUP BY project_id, project_type, group_id -- To get unique
        ),
        -- Calculated area by task_groups
        task_group_metadata as ({TASK_GROUP_METADATA_QUERY}),
        -- Aggregate data by user-group
        user_group_data as (
            SELECT
                MS.project_id,
                MS.group_id,
                MS.user_id,
                MSUR.user_group_id,
                MS.start_time::date as timestamp_date,
                LEAST(
                    EXTRACT(EPOCH FROM (MS.end_time - MS.start_time)),
                    TG.time_spent_max_allowed
                ) as time_spent_sec,
                MS.items_count as task_count,
                Coalesce(TG.total_task_group_area, 0) as area_swiped
            FROM mapping_sessions_user_groups MSUR
                INNER JOIN mapping_sessions MS USING (mapping_session_id)
                LEFT JOIN task_group_metadata TG USING (project_id, group_id)
            WHERE
                MS.start_time >= %(from_date)s
                AND MS.start_time < %(until_date)s
        ),
        -- Additional aggregate by timestamp_date
        user_group_agg_data as (
          SELECT
            project_id,
            user_id,
            user_group_id,
            timestamp_date,
            COALESCE(SUM(time_spent_sec), 0) as total_time,
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
            timestamp_min = MappingSession.objects.aggregate(
                timestamp_min=models.Min("start_time")
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
