-- https://docs.google.com/spreadsheets/d/1g92Rj02LVqvYBFmdnf5CBs8IwuD0GjXP0b1A-H9SvQY/edit#gid=0

WITH
    -- Collect user_group_id
    cq_user_group_ids as (
        SELECT
            user_groups.user_group_id
        FROM user_groups
        WHERE user_groups.name in (
            'Amazon',
            'Cisco',
            'Grainger',
            'Hewlett Packard Enterprise',
            'HP Inc.',
            'Intel',
            'Lenovo',
            'Mastercard',
            'PwC',
            'Assurant',
            'Microsoft',
            'Paramount Global',
            'Flex',
            'Rodan + Fields',
            'Pitney Bowes',
            'Lockheed Martin Corporation',
            'Fanatics',
            'Zurich NA',
            'Triumph Group',
            'Leonardo DRS',
            'McKinsey & Co.',
            'Pyramid Systems'
        )
    ),
    -- Collect user_group_id+user_id
    cq_user_group_ids_and_user_ids as (
        SELECT
            user_group_id,
            user_id
        FROM user_groups_user_memberships
        WHERE
            user_group_id in (SELECT * FROM cq_user_group_ids)
            AND is_active is True
    )
-- Insert all user_id mapping session (Year: 2022+) to user_group_id
INSERT INTO mapping_sessions_user_groups(
  mapping_session_id,
  user_group_id
)
(
  SELECT
    MS.mapping_session_id,
    CQ_UG_IDS.user_group_id
  FROM mapping_sessions MS
      JOIN cq_user_group_ids_and_user_ids CQ_UG_IDS USING (user_id)
  WHERE MS.end_time >= '2022-01-01'
) ON CONFLICT (mapping_session_id, user_group_id) DO NOTHING;

-- To update aggregated data: docker-compose exec django ./manage.py update_aggregated_data
-- This table is maintaned using django
-- type = 1 = USER_GROUP
-- type = 0 = USER
-- value = date from when the data is calculated >= 2022-01-01
UPDATE aggregated_aggregatedtracking
SET "value" = '2022-01-01'
WHERE "type" in (0, 1);
