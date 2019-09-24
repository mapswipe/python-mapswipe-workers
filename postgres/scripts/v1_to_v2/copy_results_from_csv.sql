/* Import v1 MapSwipe data from csv to */
/* the v2 MapSwipe database. */
/* Make sure the v1 data is v2 conform */
/* otherwise default to NULL value. */
/* Goal: assign results based on tasks to a group */
/* Problem: there are tasks belonging to 2 different groups */

CREATE TEMP TABLE v1_results(
    project_id varchar,
    group_id varchar DEFAULT NULL,
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
\copy v1_results(project_id, task_id, user_id, timeint, info) FROM results.csv WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

-- Results were stored in the "info" attribute as json.
UPDATE v1_results
SET result = CAST(info ->> 'result' AS INTEGER)
WHERE result IS NULL;

UPDATE v1_results
SET timestamp = TO_TIMESTAMP(timeint/1000);

/* Create duplicated flag for tasks*/
ALTER TABLE
    tasks
ADD COLUMN
    duplicated boolean DEFAULT false;

/* Set duplicated tasks */
/* (tasks with same ID and geometry occurring in two different groups) */
UPDATE
    tasks t1
SET
    duplicated = true
FROM
    tasks t2
WHERE
    t1.task_id = t2.task_id
    AND t1.project_id = t2.project_id
    AND t1.group_id != t2.group_id;

/* Set group_id of v1_results for non-duplicated tasks */
UPDATE
    v1_results r
SET
    group_id = t.group_id
FROM
    tasks t
WHERE
    r.project_id = t.project_id
    AND r.task_id = t.task_id
    AND t.duplicated = false;

/* distribute results of duplicated tasks */
/* to a group with same user and existing non-duplicated tasks of this group and user. */
UPDATE
    v1_results r1
SET
    group_id = t.group_id
FROM
    tasks t
WHERE
    r1.project_id = t.project_id
    AND r1.task_id = t.task_id
    AND t.duplicated = true
    AND r1.user_id IN (
        SELECT r2.user_id
        FROM v1_results r2, tasks t2
        WHERE
            r2.project_id = t2.project_id
            AND r2.task_id = t2.task_id
            AND t2.duplicated = false
            AND r2.group_id = t.group_id);

/* delete results of duplicated task */
/* which could not be assigned to a group. */
DELETE FROM v1_results
WHERE group_id IS NULL;

/* Insert or update data of temp table to the permant table. */
/* Generate 0 results. */
WITH user_results AS(
    WITH user_tasks AS(
        WITH user_groups AS(
            SELECT r.user_id, r.group_id, r.project_id, r.timestamp
            FROM v1_results r
            GROUP BY r.group_id, r.user_id, r.project_id, r.timestamp
        )
        SELECT t.task_id, ug.*
        FROM tasks t, user_groups ug
        WHERE t.group_id = ug.group_id
        AND t.project_id = ug.project_id
    )
    SELECT
        ut.*,
        CASE
            WHEN r.result >= 0 THEN r.result
            ELSE 0
        END as result
    FROM
        user_tasks ut
    LEFT JOIN
        v1_results r
    ON
        r.task_id = ut.task_id
        AND r.group_id = ut.group_id
        AND r.user_id = ut.user_id
        AND r.project_id = ut.project_id
)
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
    user_results
ON CONFLICT (project_id, group_id, task_id, user_id) DO NOTHING;
