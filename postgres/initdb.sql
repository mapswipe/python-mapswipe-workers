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

CREATE VIEW IF NOT EXISTS aggregated_results AS
select
    *
    ,round("0_count"::numeric/total_count::numeric, 3) as "0_share"
    ,round("1_count"::numeric/total_count::numeric, 3) as "1_share"
    ,round("2_count"::numeric/total_count::numeric, 3) as "2_share"
    ,round("3_count"::numeric/total_count::numeric, 3) as "3_share"
    ,CASE WHEN total_count = 1 THEN 1.0	ELSE (
      round(
          ((1.0 / (total_count::numeric * (total_count::numeric - 1.0)))
          *
          (
          (("0_count"::numeric ^ 2.0) - "0_count"::numeric)
          +
          (("1_count"::numeric ^ 2.0) - "1_count"::numeric)
          +
          (("2_count"::numeric ^ 2.0) - "2_count"::numeric)
          +
          (("3_count"::numeric ^ 2.0) - "3_count"::numeric)
          ))
      ,3)
    ) END as agreement
from
(
	select
		project_id
		,group_id
		,task_id
		,count(*) as total_count
		,sum(CASE WHEN result = 0 THEN 1 ELSE 0	END) AS "0_count"
		,sum(CASE WHEN result = 1 THEN 1 ELSE 0	END) AS "1_count"
		,sum(CASE WHEN result = 2 THEN 1 ELSE 0	END) AS "2_count"
		,sum(CASE WHEN result = 3 THEN 1 ELSE 0	END) AS "3_count"
	from
		results
	group by
		project_id, group_id, task_id
) as foo

-- create a read-only user for backups
CREATE USER backup WITH PASSWORD 'backupuserpassword';
GRANT CONNECT ON DATABASE mapswipe TO backup;
GRANT USAGE ON SCHEMA public TO backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup;
