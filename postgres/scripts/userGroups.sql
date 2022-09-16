-- DROP TABLE IF EXISTS results_user_groups_temp;
-- DROP TABLE IF EXISTS user_groups_temp;
-- DROP TABLE IF EXISTS user_groups_user_memberships_temp;
-- DROP TABLE IF EXISTS user_groups_user_memberships;
-- DROP TABLE IF EXISTS results_user_groups;
-- DROP TABLE IF EXISTS user_groups_membership_logs;
-- DROP TABLE IF EXISTS user_groups_membership_logs_temp;
-- DROP TABLE IF EXISTS user_groups;
-- ALTER TABLE projects DROP COLUMN organization_name;
-- ALTER TABLE users DROP COLUMN updated_at;
-- ALTER TABLE users_temp DROP COLUMN updated_at;
-- DROP MATERIALIZED VIEW aggregated_project_user_timestampe__task_count_total_time;
-- DROP MATERIALIZED VIEW aggregated_project_user_group_timestamp__task_count_total_time;


---- User Group Tables
CREATE TABLE IF NOT EXISTS user_groups (
    user_group_id varchar,
    name varchar,
    description text,
    created_by_id varchar,
    created_at timestamp,
    archived_by_id varchar,
    archived_at timestamp,
    is_archived boolean,
    PRIMARY KEY (user_group_id),
    FOREIGN KEY (created_by_id) REFERENCES users (user_id),
    FOREIGN KEY (archived_by_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS user_groups_temp (
    user_group_id varchar,
    name varchar,
    description text,
    created_by_id varchar,
    created_at timestamp,
    archived_by_id varchar,
    archived_at timestamp,
    is_archived boolean
);

CREATE TABLE IF NOT EXISTS user_groups_user_memberships (
    user_group_id varchar,
    user_id varchar,
    is_active boolean,
    PRIMARY KEY (user_group_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (user_group_id) REFERENCES user_groups (user_group_id)
);

CREATE TABLE IF NOT EXISTS user_groups_user_memberships_temp (
    user_group_id varchar,
    user_id varchar
);

-- Used to group results by user groups
CREATE TABLE IF NOT EXISTS results_user_groups (
    -- result primary key (not using task_id as it is a flat field in results)
    project_id varchar,
    group_id varchar,
    user_id varchar,
    -- user group primary key
    user_group_id varchar,
    PRIMARY KEY (project_id, group_id, user_id, user_group_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (user_group_id) REFERENCES user_groups (user_group_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id)
);

-- create table for user_group_results import through csv
CREATE TABLE IF NOT EXISTS results_user_groups_temp (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    user_group_id varchar
);


-- Track user group memberships actions
CREATE TYPE membership_action AS ENUM ('join', 'leave');

CREATE TABLE IF NOT EXISTS user_groups_membership_logs (
    membership_id varchar,
    user_group_id varchar,
    user_id varchar,
    action MEMBERSHIP_ACTION,
    "timestamp" timestamp,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (user_group_id) REFERENCES user_groups (user_group_id)
);

CREATE TABLE IF NOT EXISTS user_groups_membership_logs_temp (
    membership_id varchar,
    user_group_id varchar,
    user_id varchar,
    action MEMBERSHIP_ACTION,
    "timestamp" timestamp
);


-- Add organization_name in projects
ALTER TABLE projects ADD COLUMN organization_name varchar;

-- Add updated_at in users
ALTER TABLE users ADD COLUMN updated_at timestamp;
ALTER TABLE users_temp ADD COLUMN updated_at timestamp;

-- TODO: Create this as table in Django
-- CREATE MATERIALIZED VIEW aggregated_project_user_timestamp__task_count_total_time AS WITH
-- tasks_data AS (
--   SELECT
--     project_id,
--     group_id,
--     task_id,
--     st_area(geom) as area
--   From
--     tasks
-- ),
-- user_group_agg_data AS (
--   SELECT
--     project_id,
--     group_id,
--     user_id,
--     ARRAY_AGG(DISTINCT user_group_id) as user_group_ids
--   FROM
--     results_user_groups
--   GROUP BY project_id, group_id, user_id
-- ),
-- user_data AS (
--   SELECT
--     R.project_id,
--     R.group_id,
--     R.user_id,
--     MAX(R.timestamp::date) as timestamp_date,
--     MAX(R.start_time) as start_time,
--     MAX(R.end_time) as end_time,
--     COUNT(DISTINCT R.task_id) as task_count,
--     SUM(T.area) as area_swiped -- TODO: use task count instead contact @safar.ligal
--   From
--     results R
--     LEFT JOIN tasks_data T USING (project_id, group_id, task_id)
--   GROUP BY R.project_id, R.group_id, R.user_id
-- )
-- SELECT
--   project_id,
--   user_id,
--   timestamp_date,
--   SUM(
--     EXTRACT( EPOCH FROM (end_time - start_time))
--   ) as total_time,
--   SUM(task_count) as task_count,
--   SUM(area_swiped) as area_swiped,
--   ugad.user_group_ids
-- FROM
--   user_data
--   LEFT JOIN user_group_agg_data ugad USING (project_id, group_id, user_id)
-- GROUP BY project_id, user_id, timestamp_date, ugad.user_group_ids;

-- TODO: Create this as table in Django
-- CREATE MATERIALIZED VIEW aggregated_project_user_group_timestamp__task_count_total_time AS
-- WITH tasks_data AS (
--   SELECT
--     project_id,
--     group_id,
--     task_id,
--     st_area(geom) as area
--   From
--     tasks
-- ),
-- user_group_data AS (
--     SELECT
--         ug.project_id,
--         ug.group_id,
--         ug.user_group_id,
--         ug.user_id,
--         MAX(R.timestamp::date) as timestamp_date,
--         MAX(R.start_time) as start_time,
--         MAX(R.end_time) as end_time,
--         COUNT(DISTINCT R.task_id) as task_count,
--         SUM(T.area) as area_swiped
--     From results_user_groups ug
--         LEFT JOIN results R USING (project_id, group_id, user_id)
--         LEFT JOIN tasks_data T USING (project_id, group_id, task_id)
--     GROUP BY ug.project_id, ug.group_id, ug.user_group_id, ug.user_id
-- )
-- SELECT
--     project_id,
--     user_id,
--     user_group_id,
--     timestamp_date,
--     SUM(
--         EXTRACT(
--             EPOCH FROM (end_time - start_time)
--         )
--     ) as total_time,
--     SUM(task_count) as task_count,
--     SUM(area_swiped) as area_swiped
-- FROM user_group_data
-- GROUP BY project_id, user_id, user_group_id, timestamp_date;
