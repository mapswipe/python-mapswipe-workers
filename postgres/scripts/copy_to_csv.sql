-- Export v1 MapSwipe data to csv.
-- Rename attributes to conform to v2.
\copy (SELECT archive, image, isfeatured AS "is_featured", lookfor AS "look_for", name, progress, projectdetails AS "project_details", project_id, project_type, state AS "status", info AS "project_type_specifics" FROM projects LIMIT 1) TO 'projects.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

\copy (SELECT project_id, group_id, count as "number_of_tasks", completedcount as "finished_count", verificationcount as "required_count", info as "project_type_specifics" FROM groups LIMIT 1) TO 'groups.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

\copy (SELECT project_id, group_id, task_id, info as "project_type_specifics" FROM tasks LIMIT 1) TO 'tasks.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

\copy (SELECT user_id, username FROM users LIMIT 1) TO 'users.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

\copy (SELECT project_id, task_id, user_id, timestamp as "timeint", info FROM results LIMIT 1) TO 'results.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);
