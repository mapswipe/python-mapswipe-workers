ALTER TABLE user_groups_user_memberships DROP COLUMN joined_at;
ALTER TABLE user_groups_user_memberships DROP COLUMN left_at;
ALTER TABLE projects ADD COLUMN organization_name varchar;
ALTER TABLE user_groups_user_memberships_temp DROP COLUMN joined_at;
ALTER TABLE user_groups_user_memberships_temp DROP COLUMN left_at;

ALTER TABLE user_groups_user_memberships ADD COLUMN action MEMBERSHIP_ACTION;
ALTER TABLE user_groups_user_memberships ADD COLUMN "timestamp" timestamp;
ALTER TABLE user_groups_user_memberships_temp ADD COLUMN action MEMBERSHIP_ACTION;
ALTER TABLE user_groups_user_memberships_temp ADD COLUMN "timestamp" timestamp;
ALTER TABLE users ADD COLUMN updated_at timestamp;
ALTER TABLE users_temp ADD COLUMN updated_at timestamp;
