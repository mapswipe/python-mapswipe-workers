-- noinspection SqlNoDataSourceInspectionForFile

CREATE TABLE IF NOT EXISTS projects (
    archive boolean,
    created timestamp,
    created_by varchar,
    image varchar,
    is_featured boolean,
    look_for varchar,
    name varchar,
    required_results int,
    progress int,
    project_details varchar,
    project_id varchar,
    project_type int,
    result_count int,
    status varchar,
    verification_number int,
    project_type_specifics json,
    PRIMARY KEY(project_id)
    );

CREATE TABLE IF NOT EXISTS groups (
    project_id varchar,
    group_id int,
    number_of_tasks int,
    finished_count int,
    required_count int,
    progress int,
    project_type_specifics json,
    PRIMARY KEY(project_id, group_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
    );

CREATE INDEX IF NOT EXISTS groups_projectid ON public.groups USING btree (group_id);
CREATE INDEX IF NOT EXISTS groups_goupid ON public.groups USING btree (project_id);

CREATE TABLE IF NOT EXISTS tasks (
    project_id varchar,
    group_id int,
    task_id varchar,
    project_type_specifics json,
    PRIMARY KEY(project_id, group_id, task_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id)
    );

CREATE INDEX IF NOT EXISTS tasks_task_id ON public.tasks USING btree (task_id);
CREATE INDEX IF NOT EXISTS tasks_groupid ON public.tasks USING btree (group_id);
CREATE INDEX IF NOT EXISTS tasks_projectid ON public.tasks USING btree (project_id);

CREATE TABLE IF NOT EXISTS users (
    user_id varchar,
    username varchar,
    created timestamp,
    PRIMARY KEY(user_id)
    );

CREATE TABLE IF NOT EXISTS results (
    project_id varchar,
    group_id int,
    user_id varchar,
    task_id varchar,
    "timestamp" timestamp,
    start_time timestamp,
    end_time timestamp,
    result int,
    PRIMARY KEY (project_id, group_id, task_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id),
    FOREIGN KEY (project_id, group_id, task_id) REFERENCES tasks (project_id, group_id, task_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    );

CREATE INDEX IF NOT EXISTS results_projectid ON public.results USING btree (project_id);
CREATE INDEX IF NOT EXISTS results_groupid ON public.results USING btree (group_id);
CREATE INDEX IF NOT EXISTS results_taskid ON public.results USING btree (task_id);
CREATE INDEX IF NOT EXISTS results_userid ON public.results USING btree (user_id);

-- create a read-only user for backups
CREATE USER backup WITH PASSWORD 'backupuserpassword';
GRANT CONNECT ON DATABASE mapswipe TO backup;
GRANT USAGE ON SCHEMA public TO backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup;

-- create views for aggregated statistics

CREATE or REPLACE VIEW aggregated_results AS
select
    *
    ,round("0_results_count"::numeric/total_results_count::numeric, 3) as "0_results_share"
    ,round("1_results_count"::numeric/total_results_count::numeric, 3) as "1_results_share"
    ,round("2_results_count"::numeric/total_results_count::numeric, 3) as "2_results_share"
    ,round("3_results_count"::numeric/total_results_count::numeric, 3) as "3_results_share"
    ,CASE WHEN total_results_count = 1 THEN 1.0	ELSE (
      round(
          ((1.0 / (total_results_count::numeric * (total_results_count::numeric - 1.0)))
          *
          (
          (("0_results_count"::numeric ^ 2.0) - "0_results_count"::numeric)
          +
          (("1_results_count"::numeric ^ 2.0) - "1_results_count"::numeric)
          +
          (("2_results_count"::numeric ^ 2.0) - "2_results_count"::numeric)
          +
          (("3_results_count"::numeric ^ 2.0) - "3_results_count"::numeric)
          ))
      ,3)
    ) END as agreement
from
(
	select
		project_id
		,group_id
		,task_id
		,count(*) as total_results_count
		,sum(CASE WHEN result = 0 THEN 1 ELSE 0	END) AS "0_results_count"
		,sum(CASE WHEN result = 1 THEN 1 ELSE 0	END) AS "1_results_count"
		,sum(CASE WHEN result = 2 THEN 1 ELSE 0	END) AS "2_results_count"
		,sum(CASE WHEN result = 3 THEN 1 ELSE 0	END) AS "3_results_count"
	from
		results
	group by
		project_id, group_id, task_id
) as foo;

CREATE or REPLACE VIEW aggregated_projects AS
SELECT
    count(*) as total_projects_count
    ,Sum(CASE WHEN progress = 100  THEN 1 ELSE 0 END) as finished_projects_count
    ,Sum(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_projects_count
    ,Sum(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive_projects_count
    ,Round(Avg(contributor_count),3) as average_contributor_count
    ,Round(Avg(progress),3) as average_progress
    ,Round(Avg(number_of_tasks),0) as average_number_of_tasks
FROM
    projects;

CREATE or REPLACE VIEW aggregated_projects_by_type AS
SELECT
    project_type
    ,count(*) as total_projects_count
    ,Sum(CASE WHEN progress = 100  THEN 1 ELSE 0 END) as finished_projects_count
    ,Sum(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_projects_count
    ,Sum(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive_projects_count
    ,Round(Avg(contributor_count),3) as average_contributor_count
    ,Round(Avg(progress),3) as average_progress
    ,Round(Avg(number_of_tasks),0) as average_number_of_tasks
FROM
    projects
GROUP BY
    project_type
ORDER BY
    project_type;

CREATE or REPLACE VIEW aggregated_users AS
SELECT
  count(*) as total_users_count
  ,Sum(CASE WHEN task_contribution_count > 0 THEN 1 ELSE 0 END) as active_users_count
  ,Sum(CASE WHEN task_contribution_count = 0 THEN 1 ELSE 0 END) as inactive_users_count
  ,round(avg(CASE WHEN task_contribution_count > 0 THEN project_contribution_count ELSE NULL END),1) as average_project_contribution_count
  ,round(avg(CASE WHEN task_contribution_count > 0 THEN group_contribution_count ELSE NULL END),1) as average_group_contribution_count
  ,round(avg(CASE WHEN task_contribution_count > 0 THEN task_contribution_count ELSE NULL END),1) as average_task_contribution_count
FROM
(
  SELECT
	distinct(users.user_id) as user_id
	,count(distinct(results.project_id)) as project_contribution_count
	,count(distinct(results.group_id)) as group_contribution_count
	,count(distinct(results.task_id)) as task_contribution_count
	,min(timestamp) as first_contribution_timestamp
	,max(timestamp) as last_contribution_timestamp
FROM
users
LEFT JOIN results ON
	users.user_id = results.user_id
GROUP BY users.user_id
) as foo;

CREATE or REPLACE VIEW aggregated_results_by_user_id AS
SELECT
	distinct(users.user_id) as user_id
	,users.username as user_name
	,count(distinct(results.project_id)) as project_contribution_count
	,count(distinct(results.group_id)) as group_contribution_count
	,count(distinct(results.task_id)) as task_contribution_count
	,min(timestamp) as first_contribution_timestamp
	,max(timestamp) as last_contribution_timestamp
FROM
users
LEFT JOIN results ON
	users.user_id = results.user_id
GROUP BY users.user_id, users.username;

CREATE or REPLACE VIEW aggregated_results_by_project_id_and_date AS
SELECT
 project_id
 ,count(*) as total_results_count
 ,count(distinct(user_id)) as total_users_count
 ,extract(year from timestamp) as year
 ,extract(month from timestamp) as month
 ,extract(day from timestamp) as day
FROM
 results
GROUP BY
 project_id, year, month, day;
