DROP TABLE IF EXISTS v2_res_by_project_group_day;
CREATE TEMP TABLE v2_res_by_project_group_day AS
SELECT
  r.project_id
  ,r.group_id
  ,Min(g.number_of_tasks) as number_of_tasks
  ,Min(g.required_count + g.finished_count) as number_of_users_required
  -- the following attributes are dynamic
  -- could also set to hour if needed, of make this a as a parameter
  ,date_trunc('day', timestamp) as day
  ,count(distinct(user_id)) as number_of_users
  ,count(distinct(user_id)) * Min(g.number_of_tasks) as number_of_results
FROM
  results as r, groups as g
WHERE
  r.project_id = g.project_id
  AND
  r.group_id = g.group_id
  AND
  -- use a single project id or a list of projects
  r.project_id in ('5519')
GROUP BY
  r.project_id
  ,r.group_id
  ,day;

DROP TABLE IF EXISTS v2_progress_by_project_group_day;
CREATE TEMP TABLE v2_progress_by_project_group_day AS
SELECT
  project_id
  ,group_id
  ,number_of_tasks
  ,number_of_users_required
  ,day
  ,number_of_users
  ,number_of_results
  ,SUM(number_of_users) OVER (PARTITION BY project_id, group_id ORDER BY day) as cum_number_of_users
  ,SUM(number_of_results) OVER (PARTITION BY project_id, group_id ORDER BY day) as cum_number_of_results
FROM
  v2_res_by_project_group_day
ORDER BY
  project_id, group_id, day;

DROP TABLE IF EXISTS v2_correct_by_project_group_day;
CREATE TEMP TABLE v2_correct_by_project_group_day AS
SELECT
  r.*
  ,CASE
	WHEN cum_number_of_users <= number_of_users_required THEN cum_number_of_users
	ELSE number_of_users_required
  END as cum_number_of_users_progress
  ,CASE
    WHEN cum_number_of_users <= number_of_users_required THEN cum_number_of_results
    ELSE cum_number_of_results - ((cum_number_of_users - number_of_users_required) * number_of_tasks)
  END as cum_number_of_results_progress
  ,CASE
    WHEN cum_number_of_users <= number_of_users_required THEN number_of_results
    WHEN (cum_number_of_users - number_of_users) < number_of_users_required THEN (number_of_users_required - (cum_number_of_users - number_of_users)) * number_of_tasks
    ELSE 0
  END as number_of_results_progress
FROM
  v2_progress_by_project_group_day as r;

SELECT
  r.project_id
  ,r.day
  ,SUM(r.number_of_results) as number_of_results
  ,SUM(r.number_of_results_progress) as number_of_results_progress
  ,SUM(SUM(r.number_of_results)) OVER (PARTITION BY r.project_id ORDER BY day) as cum_number_of_results
  ,SUM(SUM(r.number_of_results_progress)) OVER (PARTITION BY r.project_id ORDER BY day) as cum_number_of_results_progress
  ,Min(p.required_results) as required_results
  ,Round(SUM(SUM(r.number_of_results_progress)) OVER (PARTITION BY r.project_id ORDER BY day) / Min(p.required_results), 3) as progress
FROM
  v2_correct_by_project_group_day as r
  ,projects as p
WHERE
  p.project_id = r.project_id
GROUP BY
  r.project_id
  ,r.day
ORDER BY
  r.project_id,
  r.day