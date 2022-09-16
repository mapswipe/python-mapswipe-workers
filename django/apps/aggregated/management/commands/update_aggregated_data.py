from django.core.management.base import BaseCommand

from apps.aggregated.models import AggregatedUserStatData, AggregatedUserGroupStatData


class Command(BaseCommand):
    def update_user_data(self):
        SQL = '''
            WITH tasks_data AS (
              SELECT
                project_id,
                group_id,
                task_id,
                ST_Area(geom::geography(GEOMETRY,4326)) as area
              From
                tasks
            ),
            user_group_agg_data AS (
              SELECT
                project_id,
                group_id,
                user_id,
              FROM
                results_user_groups
              GROUP BY
                project_id,
                group_id,
                user_id
            ),
            user_data AS (
              SELECT
                R.project_id,
                R.group_id,
                R.user_id,
                MAX(R.timestamp:: date) as timestamp_date,
                MAX(R.start_time) as start_time,
                MAX(R.end_time) as end_time,
                COUNT(DISTINCT R.task_id) as task_count,
                SUM(T.area) as area_swiped
              From
                results R
                LEFT JOIN tasks_data T USING (project_id, group_id, task_id)
              -- WHERE user_id = 'HNLcgITQMdPqI7SvgTwKpH8t9o03'
              GROUP BY
                R.project_id,
                R.group_id,
                R.user_id
            )
            SELECT
              project_id,
              user_id,
              timestamp_date,
              SUM(
                EXTRACT(
                  EPOCH
                  FROM
                    (end_time - start_time)
                )
              ) as total_time,
              SUM(task_count) as task_count,
              SUM(area_swiped) as area_swiped
            FROM
              user_data
              LEFT JOIN user_group_agg_data ugad USING (project_id, group_id, user_id)
            GROUP BY
              project_id,
              user_id,
              timestamp_date;
        '''
        print(SQL)

    def update_user_group_data(self):
        SQL = '''
            WITH tasks_data AS (
              SELECT
                task_id,
                ST_Area(geom::geography(GEOMETRY,4326)) as area
              From
                tasks
            ),
            user_group_data AS (
                SELECT
                    ug.project_id,
                    ug.group_id,
                    ug.user_group_id,
                    ug.user_id,
                    MAX(R.timestamp::date) as timestamp_date,
                    MAX(R.start_time) as start_time,
                    MAX(R.end_time) as end_time,
                    COUNT(DISTINCT R.task_id) as task_count,
                    SUM(T.area) as area_swiped
                From results_user_groups ug
                    LEFT JOIN results R USING (project_id, group_id, user_id)
                    LEFT JOIN tasks_data T USING (task_id)
                GROUP BY ug.project_id, ug.group_id, ug.user_group_id, ug.user_id
            )
            SELECT
                project_id,
                user_id,
                user_group_id,
                timestamp_date,
                SUM(
                    EXTRACT(
                        EPOCH FROM (end_time - start_time)
                    )
                ) as total_time,
                SUM(task_count) as task_count,
                SUM(area_swiped) as area_swiped
            FROM user_group_data
            GROUP BY project_id, user_id, user_group_id, timestamp_date;
        '''
        print(SQL)

    def handle(self, **_):
        print(AggregatedUserStatData)
        print(AggregatedUserGroupStatData)
