-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.

CREATE TEMP TABLE v1_users (
    user_id varchar,
    username varchar,
    created timestamp DEFAULT NULL
);

-- Has to be in one line otherwise syntax error
\copy v1_users(user_id, username) FROM 'users.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

-- Insert or update data of temp table to the permant table.
INSERT INTO
  users(
    user_id,
    username,
    created
  )
SELECT
  user_id,
  username,
  created
FROM
  v1_users
ON CONFLICT (user_id) DO NOTHING;
