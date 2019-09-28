-- Export v1 MapSwipe data to csv.
-- Rename attributes to conform to v2.
\copy (SELECT user_id, username FROM users) TO users.csv WITH (FORMAT CSV, DELIMITER ",", HEADER TRUE);
\copy (SELECT project_id, task_id, user_id, timestamp as "timeint", info FROM results WHERE project_id in (SELECT project_id FROM projects GROUP BY project_id) AND user_id in (SELECT user_id FROM users)) TO results.csv WITH (FORMAT CSV, DELIMITER ",", HEADER TRUE);