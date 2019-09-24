-- create views for statistics
-- projects
-- aggregated_projects
-- aggregated_projects

CREATE OR REPLACE VIEW aggregated_projects AS
SELECT
  count(*) AS total_projects_count,
  sum(CASE
          WHEN progress = 100 THEN 1
          ELSE 0
      END) AS finished_projects_count,
  sum(CASE
          WHEN status = 'active' THEN 1
          ELSE 0
      END) AS active_projects_count,
  sum(CASE
          WHEN status = 'inactive' THEN 1
          ELSE 0
      END) AS inactive_projects_count,
  round(avg(progress), 3) AS average_progress,
  round(avg(required_results), 0) AS average_number_of_tasks
FROM projects;

-- aggregated_projects_by_project_type

CREATE OR REPLACE VIEW aggregated_projects_by_project_type AS
SELECT
  project_type,
  count(*) AS total_projects_count,
  sum(CASE
          WHEN progress = 100 THEN 1
          ELSE 0
      END) AS finished_projects_count,
  sum(CASE
          WHEN status = 'active' THEN 1
          ELSE 0
      END) AS active_projects_count,
  sum(CASE
          WHEN status = 'inactive' THEN 1
          ELSE 0
      END) AS inactive_projects_count,
  round(avg(progress), 3) AS average_progress,
  round(avg(required_results), 0) AS average_number_of_tasks
FROM projects
GROUP BY project_type
ORDER BY project_type;

-- users
-- aggregated_users

CREATE OR REPLACE VIEW aggregated_users AS
SELECT
  count(*) AS total_users_count,
  sum(CASE
          WHEN task_contribution_count > 0 THEN 1
          ELSE 0
      END) AS active_users_count,
  sum(CASE
          WHEN task_contribution_count = 0 THEN 1
          ELSE 0
      END) AS inactive_users_count,
  round(avg(CASE
                WHEN task_contribution_count > 0 THEN project_contribution_count
                ELSE NULL
            END), 1) AS average_project_contribution_count,
  round(avg(CASE
                WHEN task_contribution_count > 0 THEN group_contribution_count
                ELSE NULL
            END), 1) AS average_group_contribution_count,
  round(avg(CASE
                WHEN task_contribution_count > 0 THEN task_contribution_count
                ELSE NULL
            END), 1) AS average_task_contribution_count
FROM
  (SELECT
     distinct(users.user_id) AS user_id,
     count(distinct(results.project_id)) AS project_contribution_count,
     count(distinct(results.group_id)) AS group_contribution_count,
     count(distinct(results.task_id)) AS task_contribution_count,
     min(TIMESTAMP) AS first_contribution_timestamp,
     max(TIMESTAMP) AS last_contribution_timestamp
   FROM users
   LEFT JOIN results ON users.user_id = results.user_id
   GROUP BY users.user_id) AS foo;

-- results
-- aggregated_results

CREATE OR REPLACE VIEW aggregated_results AS
SELECT
  count(distinct(project_id)) AS projects_count,
  count(distinct(group_id, project_id)) AS groups_count,
  count(distinct(task_id, group_id, project_id)) AS tasks_count,
  count(distinct(user_id)) AS users_count,
  count(*) AS total_results_count,
  sum(CASE
          WHEN RESULT = 0 THEN 1
          ELSE 0
      END) AS "0_results_count",
  sum(CASE
          WHEN RESULT = 1 THEN 1
          ELSE 0
      END) AS "1_results_count",
  sum(CASE
          WHEN RESULT = 2 THEN 1
          ELSE 0
      END) AS "2_results_count",
  sum(CASE
          WHEN RESULT = 3 THEN 1
          ELSE 0
      END) AS "3_results_count",
  round(sum(CASE
                WHEN RESULT = 0 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "0_results_share",
  round(sum(CASE
                WHEN RESULT = 1 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "1_results_share",
  round(sum(CASE
                WHEN RESULT = 2 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "2_results_share",
  round(sum(CASE
                WHEN RESULT = 3 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "3_results_share",
  min(TIMESTAMP) AS first_timestamp,
  max(TIMESTAMP) AS last_timestamp
FROM results;

-- aggregated_results_by_task_id

CREATE OR REPLACE VIEW aggregated_results_by_task_id AS
SELECT
  *,
  CASE
      WHEN total_results_count = 1 THEN 1.0
      ELSE (round(((1.0 / (total_results_count::numeric * (total_results_count::numeric - 1.0))) * ((("0_results_count"::numeric ^ 2.0) - "0_results_count"::numeric) + (("1_results_count"::numeric ^ 2.0) - "1_results_count"::numeric) + (("2_results_count"::numeric ^ 2.0) - "2_results_count"::numeric) + (("3_results_count"::numeric ^ 2.0) - "3_results_count"::numeric))),3))
  END AS agreement
FROM
  (SELECT
     project_id,
     group_id,
     task_id,
     count(*) AS total_results_count,
     sum(CASE
             WHEN RESULT = 0 THEN 1
             ELSE 0
         END) AS "0_results_count",
     sum(CASE
             WHEN RESULT = 1 THEN 1
             ELSE 0
         END) AS "1_results_count",
     sum(CASE
             WHEN RESULT = 2 THEN 1
             ELSE 0
         END) AS "2_results_count",
     sum(CASE
             WHEN RESULT = 3 THEN 1
             ELSE 0
         END) AS "3_results_count",
     round(sum(CASE
                   WHEN RESULT = 0 THEN 1
                   ELSE 0
               END)::numeric / count(*), 3) AS "0_results_share",
     round(sum(CASE
                   WHEN RESULT = 1 THEN 1
                   ELSE 0
               END)::numeric / count(*), 3) AS "1_results_share",
     round(sum(CASE
                   WHEN RESULT = 2 THEN 1
                   ELSE 0
               END)::numeric / count(*), 3) AS "2_results_share",
     round(sum(CASE
                   WHEN RESULT = 3 THEN 1
                   ELSE 0
               END)::numeric / count(*), 3) AS "3_results_share",
     min(TIMESTAMP) AS first_timestamp,
     max(TIMESTAMP) AS last_timestamp
   FROM results
   GROUP BY
     project_id,
     group_id,
     task_id) AS foo;

-- aggregated_results_by_project_id

CREATE OR REPLACE VIEW aggregated_results_by_project_id AS
SELECT
  project_id,
  count(distinct(group_id, project_id)) AS groups_count,
  count(distinct(task_id, group_id, project_id)) AS tasks_count,
  count(distinct(user_id)) AS users_count,
  count(*) AS total_results_count,
  sum(CASE
          WHEN RESULT = 0 THEN 1
          ELSE 0
      END) AS "0_results_count",
  sum(CASE
          WHEN RESULT = 1 THEN 1
          ELSE 0
      END) AS "1_results_count",
  sum(CASE
          WHEN RESULT = 2 THEN 1
          ELSE 0
      END) AS "2_results_count",
  sum(CASE
          WHEN RESULT = 3 THEN 1
          ELSE 0
      END) AS "3_results_count",
  round(sum(CASE
                WHEN RESULT = 0 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "0_results_share",
  round(sum(CASE
                WHEN RESULT = 1 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "1_results_share",
  round(sum(CASE
                WHEN RESULT = 2 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "2_results_share",
  round(sum(CASE
                WHEN RESULT = 3 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "3_results_share",
  min(TIMESTAMP) AS first_timestamp,
  max(TIMESTAMP) AS last_timestamp
FROM results
GROUP BY project_id;

-- aggregated_results_by_project_id_and_date

CREATE OR REPLACE VIEW aggregated_results_by_project_id_and_date AS
SELECT
  project_id,
  date_trunc('day'::text, results."timestamp") AS DAY,
  count(distinct(group_id, project_id)) AS groups_count,
  count(distinct(task_id, group_id, project_id)) AS tasks_count,
  count(distinct(user_id)) AS users_count,
  count(*) AS total_results_count,
  sum(CASE
          WHEN RESULT = 0 THEN 1
          ELSE 0
      END) AS "0_results_count",
  sum(CASE
          WHEN RESULT = 1 THEN 1
          ELSE 0
      END) AS "1_results_count",
  sum(CASE
          WHEN RESULT = 2 THEN 1
          ELSE 0
      END) AS "2_results_count",
  sum(CASE
          WHEN RESULT = 3 THEN 1
          ELSE 0
      END) AS "3_results_count",
  round(sum(CASE
                WHEN RESULT = 0 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "0_results_share",
  round(sum(CASE
                WHEN RESULT = 1 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "1_results_share",
  round(sum(CASE
                WHEN RESULT = 2 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "2_results_share",
  round(sum(CASE
                WHEN RESULT = 3 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "3_results_share",
  min(TIMESTAMP) AS first_timestamp,
  max(TIMESTAMP) AS last_timestamp
FROM results
GROUP BY
  project_id,
  DAY;

-- aggregated_results_by_user_id

CREATE OR REPLACE VIEW aggregated_results_by_user_id AS
SELECT
  user_id,
  count(distinct(project_id)) AS projects_count,
  count(distinct(group_id, project_id)) AS groups_count,
  count(distinct(task_id, group_id, project_id)) AS tasks_count,
  count(*) AS total_results_count,
  sum(CASE
          WHEN RESULT = 0 THEN 1
          ELSE 0
      END) AS "0_results_count",
  sum(CASE
          WHEN RESULT = 1 THEN 1
          ELSE 0
      END) AS "1_results_count",
  sum(CASE
          WHEN RESULT = 2 THEN 1
          ELSE 0
      END) AS "2_results_count",
  sum(CASE
          WHEN RESULT = 3 THEN 1
          ELSE 0
      END) AS "3_results_count",
  round(sum(CASE
                WHEN RESULT = 0 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "0_results_share",
  round(sum(CASE
                WHEN RESULT = 1 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "1_results_share",
  round(sum(CASE
                WHEN RESULT = 2 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "2_results_share",
  round(sum(CASE
                WHEN RESULT = 3 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "3_results_share",
  min(TIMESTAMP) AS first_timestamp,
  max(TIMESTAMP) AS last_timestamp
FROM results
GROUP BY user_id;

-- aggregated_results_by_user_id_and_date

CREATE OR REPLACE VIEW aggregated_results_by_user_id_and_date AS
SELECT
  user_id,
  date_trunc('day'::text, results."timestamp") AS DAY,
  count(distinct(project_id)) AS projects_count,
  count(distinct(group_id, project_id)) AS groups_count,
  count(distinct(task_id, group_id, project_id)) AS tasks_count,
  count(*) AS total_results_count,
  sum(CASE
          WHEN RESULT = 0 THEN 1
          ELSE 0
      END) AS "0_results_count",
  sum(CASE
          WHEN RESULT = 1 THEN 1
          ELSE 0
      END) AS "1_results_count",
  sum(CASE
          WHEN RESULT = 2 THEN 1
          ELSE 0
      END) AS "2_results_count",
  sum(CASE
          WHEN RESULT = 3 THEN 1
          ELSE 0
      END) AS "3_results_count",
  round(sum(CASE
                WHEN RESULT = 0 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "0_results_share",
  round(sum(CASE
                WHEN RESULT = 1 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "1_results_share",
  round(sum(CASE
                WHEN RESULT = 2 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "2_results_share",
  round(sum(CASE
                WHEN RESULT = 3 THEN 1
                ELSE 0
            END)::numeric / count(*), 3) AS "3_results_share",
  min(TIMESTAMP) AS first_timestamp,
  max(TIMESTAMP) AS last_timestamp
FROM results
GROUP BY
  user_id,
  DAY;

-- aggregated_progress_by_project_id

CREATE OR REPLACE VIEW aggregated_progress_by_project_id AS
SELECT
  projects.project_id,
  projects.required_results,
  sum(group_progress.groups_finished_count) AS groups_finished_count,
  sum(group_progress.results_finished_count) AS results_finished_count,
  sum(group_progress.results_finished_count_for_progress) AS results_finished_count_for_progress,
  round(sum(group_progress.results_finished_count_for_progress) / projects.required_results::numeric, 3) AS progress
FROM projects
LEFT JOIN
  (SELECT
     results.group_id,
     results.project_id,
     date_trunc('day', TIMESTAMP) AS DAY,
     count(distinct(user_id)) AS groups_finished_count,
     count(distinct(user_id)) * max(groups.number_of_tasks) AS results_finished_count,
     CASE
         WHEN count(distinct(user_id)) > max(groups.required_count) THEN max(groups.required_count) * max(groups.number_of_tasks)
         ELSE count(distinct(user_id)) * max(groups.number_of_tasks)
     END AS results_finished_count_for_progress,
     max(groups.required_count) * max(groups.number_of_tasks) AS results_required_count
   FROM
     results,
     groups
   WHERE results.group_id = groups.group_id
     AND results.project_id = groups.project_id
   GROUP BY
     results.group_id,
     results.project_id,
     DAY) AS group_progress ON group_progress.project_id = projects.project_id
GROUP BY projects.project_id
ORDER BY projects.project_id;

-- aggregated_progress_by_project_id_and_date

CREATE VIEW aggregated_progress_by_project_id_and_date AS
SELECT
  projects.project_id,
  projects.required_results,
  group_progress.day,
  sum(group_progress.groups_finished_count) AS groups_finished_count,
  sum(sum(group_progress.groups_finished_count)) OVER
  (PARTITION BY projects.project_id
   ORDER BY DAY) AS cumulative_groups_finished_count,
  sum(group_progress.results_finished_count) AS results_finished_count,
  sum(sum(group_progress.results_finished_count)) OVER
  (PARTITION BY projects.project_id
   ORDER BY DAY) AS cumulative_results_finished_count,
  sum(group_progress.results_finished_count_for_progress) AS results_finished_count_for_progress,
  sum(sum(group_progress.results_finished_count_for_progress)) OVER
  (PARTITION BY projects.project_id
   ORDER BY DAY) AS cumulative_results_finished_count_for_progress,
  round(sum(sum(group_progress.results_finished_count_for_progress)) OVER (PARTITION BY projects.project_id
                                                                           ORDER BY DAY) / projects.required_results::numeric, 3) AS progress
FROM projects
LEFT JOIN
  (SELECT
     results.group_id,
     results.project_id,
     date_trunc('day', TIMESTAMP) AS DAY,
     count(distinct(user_id)) AS groups_finished_count,
     count(distinct(user_id)) * max(groups.number_of_tasks) AS results_finished_count,
     CASE
         WHEN count(distinct(user_id)) > max(groups.required_count) THEN max(groups.required_count) * max(groups.number_of_tasks)
         ELSE count(distinct(user_id)) * max(groups.number_of_tasks)
     END AS results_finished_count_for_progress,
     max(groups.required_count) * max(groups.number_of_tasks) AS results_required_count
   FROM
     results,
     groups
   WHERE results.group_id = groups.group_id
     AND results.project_id = groups.project_id
   GROUP BY
     results.group_id,
     results.project_id,
     DAY) AS group_progress ON group_progress.project_id = projects.project_id
GROUP BY
  projects.project_id,
  DAY
ORDER BY
  projects.project_id,
  DAY;
