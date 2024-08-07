-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.

CREATE TEMP TABLE v1_groups (
    project_id varchar,
    v1_group_id int,
    group_id varchar,
    number_of_tasks int,
    finished_count int,
    required_count int,
    progress int DEFAULT NULL,
    project_type_specifics json
);

-- Has to be in one line otherwise syntax error
\copy v1_groups(project_id, v1_group_id, number_of_tasks, finished_count, required_count, project_type_specifics) FROM groups.csv WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

-- (Convert old to new data structure).
-- verification_count (old name for required_count) was static.
UPDATE v1_groups
SET required_count = required_count - finished_count;

UPDATE v1_groups
SET progress = 100
WHERE required_count <= 0;

UPDATE v1_groups
SET group_id = cast(v1_group_id as varchar);

/* UPDATE groups */
/* SET (finished_count, required_count, progress) = */
/*         (SELECT finished_count, required_count, progress */
/*         FROM v1_groups */
/*         WHERE groups.group_id = v1_groups.group_id */
/*         AND groups.project_id = v1_groups.project_id); */

-- Insert or update data of temp table to the permant table.
-- Note that the special excluded table is used to
-- reference values originally proposed for insertion
INSERT INTO
  groups(
    project_id,
    group_id,
    number_of_tasks,
    finished_count,
    required_count,
    progress,
    project_type_specifics
  )
SELECT
  project_id,
  group_id,
  number_of_tasks,
  finished_count,
  required_count,
  progress,
  project_type_specifics
FROM
  v1_groups
ON CONFLICT (project_id, group_id) DO NOTHING;
