-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.

CREATE TEMP TABLE v1_tasks (
    project_id varchar,
    group_id int,
    task_id varchar,
    geom geometry(MULTIPOLYGON,4326) DEFAULT NULL,
    wkt varchar,
    project_type_specifics json
);

-- Has to be in one line otherwise syntax error
\copy v1_tasks(project_id, group_id, task_id, project_type_specifics) FROM tasks.csv WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);


-- Extract geometry (wkt) from project type specifics attribute (json)
UPDATE v1_tasks t1
SET wkt = (SELECT project_type_specifics->>'wkt');

-- Convert geometry to postgis geometry type.
UPDATE v1_tasks
SET geom = ST_Force2D(ST_Multi(ST_GeomFromText(wkt, 4326)));

-- Insert or update data of temp table to the permant table.
-- Note that the special excluded table is used to
-- reference values originally proposed for insertion
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
