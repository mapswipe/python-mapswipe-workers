-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.

CREATE TEMP TABLE v1_groups (
    project_id varchar,
    group_id int,
    number_of_tasks int,
    finished_count int,
    required_count int,
    progress int DEFAULT NULL,
    project_type_specifics json
);

-- Has to be in one line otherwise syntax error
\copy v1_groups(project_id, group_id, number_of_tasks, finished_count, required_count, project_type_specifics) FROM groups.csv WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

-- (Convert old to new data structure).
-- verification_count (old name for required_count) was static.
UPDATE v1_groups
SET required_count = required_count - finished_count;

UPDATE v1_groups
SET progress = 100
WHERE required_count <= 0;

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
ON CONFLICT (project_id, group_id) DO UPDATE
SET
  finished_count = excluded.finished_count,
  required_count = excluded.required_count,
  progress = excluded.progress
;
