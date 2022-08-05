ALTER TABLE projects ADD COLUMN organization_id VARCHAR;
ALTER TABLE projects ADD CONSTRAINT projects_fkey FOREIGN KEY (organization_id) REFERENCES organizations (organization_id);