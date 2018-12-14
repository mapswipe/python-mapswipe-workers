-- noinspection SqlNoDataSourceInspectionForFile

CREATE TABLE IF NOT EXISTS projects (
  contributors int
  ,groupAverage int
  ,project_id int
  ,image varchar
  ,importKey varchar
  ,isFeatured boolean
  ,lookFor varchar
  ,name varchar
  ,progress int
  ,projectDetails varchar
  ,state int
  ,verificationCount int
  ,project_type int
  ,info json

  ,CONSTRAINT projects_pkey PRIMARY KEY(project_id)
);

CREATE TABLE IF NOT EXISTS imports (
  import_id varchar
  ,info json

  ,CONSTRAINT imports_pkey PRIMARY KEY(import_id)
);

CREATE TABLE IF NOT EXISTS tasks (
  task_id varchar
  ,group_id int
  ,project_id int
  ,info json

  ,CONSTRAINT tasks_pkey PRIMARY KEY(task_id, group_id, project_id)
);

CREATE TABLE IF NOT EXISTS groups (
  project_id int
  ,group_id int
  ,count int
  ,completedCount int
  ,info json

  ,CONSTRAINT groups_pkey PRIMARY KEY(project_id, group_id)
);

CREATE TABLE IF NOT EXISTS users (
  user_id varchar
  ,contributions int
  ,distance double precision
  ,username varchar

  ,CONSTRAINT users_pkey PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS results (
  task_id character varying NOT NULL
  ,project_id integer NOT NULL
  ,user_id character varying NOT NULL
  ,"timestamp" bigint
  ,info json
  ,duplicates integer

  ,CONSTRAINT results_pkey PRIMARY KEY (task_id, user_id, project_id)
);

CREATE TABLE IF NOT EXISTS progress(
  project_id int
  ,contributors int
  ,progress int
  ,timestamp bigint

);


