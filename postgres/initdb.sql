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

-- create table for results import through csv
CREATE TABLE IF NOT EXISTS results_temp (
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


-- create a read-only user for backups
CREATE USER backup WITH PASSWORD 'backupuserpassword';
GRANT CONNECT ON DATABASE mapswipe TO backup;
GRANT USAGE ON SCHEMA public TO backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup;

-- create views for statistics
-- projects
-- aggregated_projects
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

-- aggregated_projects_by_project_type
CREATE or REPLACE VIEW aggregated_projects_by_project_type AS
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

-- users
-- aggregated_users
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

-- results
-- aggregated_results
CREATE or REPLACE VIEW aggregated_results AS
select
	count(distinct(project_id)) as  projects_count
	,count(distinct(group_id, project_id)) as groups_count
	,count(distinct(task_id,group_id,project_id)) as tasks_count
	,count(distinct(user_id)) as users_count
	,count(*) as total_results_count
	,sum(CASE WHEN result = 0 THEN 1 ELSE 0	END) AS "0_results_count"
	,sum(CASE WHEN result = 1 THEN 1 ELSE 0	END) AS "1_results_count"
	,sum(CASE WHEN result = 2 THEN 1 ELSE 0	END) AS "2_results_count"
	,sum(CASE WHEN result = 3 THEN 1 ELSE 0	END) AS "3_results_count"
	,round(sum(CASE WHEN result = 0 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "0_results_share"
	,round(sum(CASE WHEN result = 1 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "1_results_share"
	,round(sum(CASE WHEN result = 2 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "2_results_share"
	,round(sum(CASE WHEN result = 3 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "3_results_share"
	,min(timestamp) as first_timestamp
	,max(timestamp) as last_timestamp
from
	results;

-- aggregated_results_by_task_id
CREATE or REPLACE VIEW aggregated_results_by_task_id AS
select
    *
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
		,round(sum(CASE WHEN result = 0 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "0_results_share"
		,round(sum(CASE WHEN result = 1 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "1_results_share"
		,round(sum(CASE WHEN result = 2 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "2_results_share"
		,round(sum(CASE WHEN result = 3 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "3_results_share"
		,min(timestamp) as first_timestamp
		,max(timestamp) as last_timestamp
	from
		results
	group by
		project_id, group_id, task_id
) as foo;

-- aggregated_results_by_project_id
CREATE or REPLACE VIEW aggregated_results_by_project_id AS
select
	project_id
	,count(distinct(group_id, project_id)) as groups_count
	,count(distinct(task_id,group_id,project_id)) as tasks_count
	,count(distinct(user_id)) as users_count
	,count(*) as total_results_count
	,sum(CASE WHEN result = 0 THEN 1 ELSE 0	END) AS "0_results_count"
	,sum(CASE WHEN result = 1 THEN 1 ELSE 0	END) AS "1_results_count"
	,sum(CASE WHEN result = 2 THEN 1 ELSE 0	END) AS "2_results_count"
	,sum(CASE WHEN result = 3 THEN 1 ELSE 0	END) AS "3_results_count"
	,round(sum(CASE WHEN result = 0 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "0_results_share"
	,round(sum(CASE WHEN result = 1 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "1_results_share"
	,round(sum(CASE WHEN result = 2 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "2_results_share"
	,round(sum(CASE WHEN result = 3 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "3_results_share"
	,min(timestamp) as first_timestamp
	,max(timestamp) as last_timestamp
from
	results
GROUP BY
	project_id;

-- aggregated_results_by_project_id_and_date
CREATE or REPLACE VIEW aggregated_results_by_project_id_and_date AS
select
	project_id
	,date_trunc('day'::text, results."timestamp") AS day
	,count(distinct(group_id, project_id)) as groups_count
	,count(distinct(task_id,group_id,project_id)) as tasks_count
	,count(distinct(user_id)) as users_count
	,count(*) as total_results_count
	,sum(CASE WHEN result = 0 THEN 1 ELSE 0	END) AS "0_results_count"
	,sum(CASE WHEN result = 1 THEN 1 ELSE 0	END) AS "1_results_count"
	,sum(CASE WHEN result = 2 THEN 1 ELSE 0	END) AS "2_results_count"
	,sum(CASE WHEN result = 3 THEN 1 ELSE 0	END) AS "3_results_count"
	,round(sum(CASE WHEN result = 0 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "0_results_share"
	,round(sum(CASE WHEN result = 1 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "1_results_share"
	,round(sum(CASE WHEN result = 2 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "2_results_share"
	,round(sum(CASE WHEN result = 3 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "3_results_share"
	,min(timestamp) as first_timestamp
	,max(timestamp) as last_timestamp
from
	results
GROUP BY
	project_id, day;

-- aggregated_results_by_user_id
CREATE or REPLACE VIEW aggregated_results_by_user_id AS
select
	user_id
	,count(distinct(project_id)) as projects_count
	,count(distinct(group_id, project_id)) as groups_count
	,count(distinct(task_id,group_id,project_id)) as tasks_count
	,count(*) as total_results_count
	,sum(CASE WHEN result = 0 THEN 1 ELSE 0	END) AS "0_results_count"
	,sum(CASE WHEN result = 1 THEN 1 ELSE 0	END) AS "1_results_count"
	,sum(CASE WHEN result = 2 THEN 1 ELSE 0	END) AS "2_results_count"
	,sum(CASE WHEN result = 3 THEN 1 ELSE 0	END) AS "3_results_count"
	,round(sum(CASE WHEN result = 0 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "0_results_share"
	,round(sum(CASE WHEN result = 1 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "1_results_share"
	,round(sum(CASE WHEN result = 2 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "2_results_share"
	,round(sum(CASE WHEN result = 3 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "3_results_share"
	,min(timestamp) as first_timestamp
	,max(timestamp) as last_timestamp
from
	results
GROUP BY
	user_id;

-- aggregated_results_by_user_id_and_date
CREATE or REPLACE VIEW aggregated_results_by_user_id_and_date AS
select
	user_id
	,date_trunc('day'::text, results."timestamp") AS day
	,count(distinct(project_id)) as projects_count
	,count(distinct(group_id, project_id)) as groups_count
	,count(distinct(task_id,group_id,project_id)) as tasks_count
	,count(*) as total_results_count
	,sum(CASE WHEN result = 0 THEN 1 ELSE 0	END) AS "0_results_count"
	,sum(CASE WHEN result = 1 THEN 1 ELSE 0	END) AS "1_results_count"
	,sum(CASE WHEN result = 2 THEN 1 ELSE 0	END) AS "2_results_count"
	,sum(CASE WHEN result = 3 THEN 1 ELSE 0	END) AS "3_results_count"
	,round(sum(CASE WHEN result = 0 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "0_results_share"
	,round(sum(CASE WHEN result = 1 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "1_results_share"
	,round(sum(CASE WHEN result = 2 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "2_results_share"
	,round(sum(CASE WHEN result = 3 THEN 1 ELSE 0	END)::numeric / count(*),3) AS "3_results_share"
	,min(timestamp) as first_timestamp
	,max(timestamp) as last_timestamp
from
	results
GROUP BY
	user_id, day;

-- aggregated_progress_by_project_id
CREATE or REPLACE VIEW aggregated_progress_by_project_id AS
SELECT
 projects.project_id
 ,projects.number_of_tasks
 ,SUM(group_progress.groups_finished_count) as groups_finished_count
 ,SUM(group_progress.results_finished_count) as results_finished_count
 ,SUM(group_progress.results_finished_count_for_progress) as results_finished_count_for_progress
 ,ROUND(
	 SUM(group_progress.results_finished_count_for_progress)
	 /
	 projects.number_of_tasks::numeric
	 	,3) as progress
FROM projects
LEFT JOIN
(
SELECT
  results.group_id
  ,results.project_id
  ,date_trunc('day', timestamp) as day
  ,count(distinct(user_id)) as groups_finished_count
  ,count(distinct(user_id)) * MAX(groups.number_of_tasks) as results_finished_count
  ,CASE
 	WHEN count(distinct(user_id)) > MAX(groups.required_count) THEN MAX(groups.required_count) * MAX(groups.number_of_tasks)
  	ELSE count(distinct(user_id)) * MAX(groups.number_of_tasks)
  END as results_finished_count_for_progress
  ,MAX(groups.required_count) * MAX(groups.number_of_tasks) as results_required_count
FROM
 results, groups
WHERE
 results.group_id = groups.group_id
 AND
 results.project_id = groups.project_id
GROUP BY
  results.group_id, results.project_id, day
) as group_progress ON
  group_progress.project_id = projects.project_id
GROUP BY
  projects.project_id
ORDER BY
  projects.project_id

-- aggregated_progress_by_project_id_and_date
CREATE VIEW aggregated_progress_by_project_id_and_date AS
SELECT
 projects.project_id
 ,projects.number_of_tasks
 ,group_progress.day
 ,SUM(group_progress.groups_finished_count) as groups_finished_count
 ,SUM(SUM(group_progress.groups_finished_count)) OVER (PARTITION BY projects.project_id ORDER BY day) as cumulative_groups_finished_count
 ,SUM(group_progress.results_finished_count) as results_finished_count
 ,SUM(SUM(group_progress.results_finished_count)) OVER (PARTITION BY projects.project_id ORDER BY day) as cumulative_results_finished_count
 ,SUM(group_progress.results_finished_count_for_progress) as results_finished_count_for_progress
 ,SUM(SUM(group_progress.results_finished_count_for_progress)) OVER (PARTITION BY projects.project_id ORDER BY day) as cumulative_results_finished_count_for_progress
 ,ROUND(
	 SUM(SUM(group_progress.results_finished_count_for_progress)) OVER (PARTITION BY projects.project_id ORDER BY day)
	 /
	 projects.number_of_tasks::numeric
	 	,3) as progress
FROM projects
LEFT JOIN
(
SELECT
  results.group_id
  ,results.project_id
  ,date_trunc('day', timestamp) as day
  ,count(distinct(user_id)) as groups_finished_count
  ,count(distinct(user_id)) * MAX(groups.number_of_tasks) as results_finished_count
  ,CASE
 	WHEN count(distinct(user_id)) > MAX(groups.required_count) THEN MAX(groups.required_count) * MAX(groups.number_of_tasks)
  	ELSE count(distinct(user_id)) * MAX(groups.number_of_tasks)
  END as results_finished_count_for_progress
  ,MAX(groups.required_count) * MAX(groups.number_of_tasks) as results_required_count
FROM
 results, groups
WHERE
 results.group_id = groups.group_id
 AND
 results.project_id = groups.project_id
GROUP BY
  results.group_id, results.project_id, day
) as group_progress ON
  group_progress.project_id = projects.project_id
GROUP BY
  projects.project_id, day
ORDER BY
  projects.project_id, day
