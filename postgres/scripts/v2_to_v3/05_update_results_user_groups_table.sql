/*
 * This script updates and tra the data from the 'results' table
 * and transfers them to the new tables
 * - 'mapping_sessions' and
 * - 'mapping_sessions_results'
 */
SET search_path = 'public';

-- Create new user_groups mapping sessions table
CREATE TABLE IF NOT EXISTS mapping_sessions_user_groups (
    mapping_session_id int8,
    user_group_id varchar,
    PRIMARY KEY (mapping_session_id, user_group_id),
    FOREIGN KEY (mapping_session_id) REFERENCES mapping_sessions (mapping_session_id),
    FOREIGN KEY (user_group_id) REFERENCES user_groups (user_group_id)
);


-- Copy data to new table
INSERT INTO mapping_sessions_user_groups
(
    SELECT
        MS.mapping_session_id,
        rug.user_group_id
    FROM results_user_groups rug
        INNER JOIN mapping_sessions MS USING (project_id, group_id, user_id)
)
ON CONFLICT do nothing;

-- NOTE: Drop old table (Do this manually after checking if all data is transferred)
-- DROP TABLE IF EXISTS results_user_groups;
