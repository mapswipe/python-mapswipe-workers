-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.

CREATE TEMP TABLE v1_results(
    project_id varchar,
    group_id int DEFAULT NULL,
    user_id varchar,
    task_id varchar,
    "timestamp" timestamp,
    timeint bigint,
    start_time timestamp DEFAULT NULL,
    end_time timestamp DEFAULT NULL,
    result int DEFAULT NULL,
    info json
);

-- Has to be in one line otherwise syntax error
\copy v1_results(project_id, task_id, user_id, timeint, info) FROM 'results.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

-- (Convert old to new data structure).
-- Results were stored in the "info" attribute as json.
UPDATE v1_results
SET result = CAST(info ->> 'result' AS INTEGER)
WHERE result IS NULL;

UPDATE v1_results
SET timestamp = TO_TIMESTAMP(timeint/1000);

-- group_id were not stored in results table.
UPDATE v1_results
SET group_id = (
  SELECT
    t.group_id
  FROM
    tasks as t,
    results as r
  WHERE
    t.task_id = r.task_id AND
    t.project_id = r.project_id
);

-- Insert or update data of temp table to the permant table.
-- Note that the special excluded table is used to
-- reference values originally proposed for insertion
INSERT INTO
  results(
    project_id,
    group_id,
    task_id,
    user_id,
    timestamp,
    result
  )
SELECT
  project_id,
  group_id,
  task_id,
  user_id,
  timestamp,
  result
FROM
  v1_results
ON CONFLICT (project_id, group_id, task_id, user_id) DO NOTHING;
