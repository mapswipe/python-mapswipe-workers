-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.

CREATE TEMP TABLE v1_tasks (
    project_id varchar,
    v1_group_id int,
    group_id varchar DEFAULT NULL,
    task_id varchar,
    project_type_specifics json,
    geom geometry(MULTIPOLYGON,4326) DEFAULT NULL
);
CREATE INDEX v1_tasks_task_id ON pg_temp_4.v1_tasks USING btree (task_id);
CREATE INDEX v1_tasks_groupid ON pg_temp_4.v1_tasks USING btree (group_id);
CREATE INDEX v1_tasks_projectid ON pg_temp_4.v1_tasks USING btree (project_id);

-- Has to be in one line otherwise syntax error
\copy v1_tasks(project_id, v1_group_id, task_id, project_type_specifics) FROM tasks.csv WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

UPDATE v1_tasks
SET group_id = cast(v1_group_id as varchar);

/* Compute geometry of tasks from x, y tile coordinates and z zoom level stored in task id*/
/* More details on the coordinates: */
/* https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system */
WITH bbox as(
    WITH lat_lon as(
        WITH pixel_coord as(
            /* Get zoom level and x and y as pixel coordinates from the task id */
            /* calculate pixel coordinates from tile coordinates */
            SELECT
                task_id,
                256 * pow(2, split_part(task_id, '-', 1)::int) as mapsize,
                split_part(task_id, '-', 2)::int * 256 as x_left,
                split_part(task_id, '-', 3)::int * 256 as y_top,
                (split_part(task_id, '-', 2)::int + 1) * 256 as x_right,
                (split_part(task_id, '-', 3)::int +1) * 256 as y_bottom
            FROM v1_tasks
        )
        /* Compute latitude, longituted from pixel coordinates at a given zoom level */
        SELECT
            task_id,
            ((x_left / mapsize) - 0.5) * 360 as lon_left,
            90 - 360 * atan(exp(-(0.5 - (y_top / mapsize)) * 2 * pi())) / pi() as lat_top,
            ((x_right / mapsize) - 0.5) * 360 as lon_right,
            90 - 360 * atan(exp(-(0.5 - (y_bottom / mapsize)) * 2 * pi())) / pi() as lat_bottom
        FROM pixel_coord
    )
    SELECT
        task_id,
        ST_SetSRID(ST_Multi(ST_Envelope(ST_MakeLine(ST_MakePoint(lon_left, lat_top), ST_MakePoint(lon_right, lat_bottom)))), 4326) as geom
    FROM lat_lon
)
UPDATE
    v1_tasks t
SET
    geom = b.geom
FROM bbox b
WHERE t.task_id = b.task_id;

/* Insert or update data of temp table to the permant table. */
INSERT INTO
  tasks(
    project_id,
    group_id,
    task_id,
    geom,
    project_type_specifics
  )
SELECT
  project_id,
  group_id,
  task_id,
  geom,
  project_type_specifics
FROM
  v1_tasks
ON CONFLICT (project_id, group_id, task_id) DO NOTHING;
