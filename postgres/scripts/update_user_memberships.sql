ALTER TABLE user_groups_user_memberships ADD COLUMN joined_at timestamp[] default '{}';
ALTER TABLE user_groups_user_memberships ADD COLUMN left_at timestamp[] default '{}';
ALTER TABLE projects ADD COLUMN organization_name varchar;
