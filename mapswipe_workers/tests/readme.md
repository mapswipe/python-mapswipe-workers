# How to add test data
Test data can be extracted from the existing MapSwipe database. This is often useful when you want to fix a bug which you observed in the production environment but are not yet exactly sure why it actually occurred in the first place.

For a given project id (e.g. `-NFNr55R_LYJvxP7wmte`) you can follow these steps:

## Export Data from Production or Development Database
To set up a project in the test environment it is very likely that you first need to set up all the data in postgres (and maybe also in Firebase).

You can extract the data into csv files like this. Make sure to adjust the where statement to your needs. If you know which part of the data is affected or causing the bug, then it's good to be very specific and filter only for these groups etc.

```
\copy (
	select created, created_by, geom, image, is_featured, look_for
		,"name" , progress , project_details , project_id , project_type
		,required_results , result_count , status , verification_number
		,project_type_specifics
		,'test_org' as organization_name
	from projects
	where project_id = '-NFNr55R_LYJvxP7wmte'
) to 'test_project.csv' delimiter E'\t' NULL '\N' csv
```

```
\copy (
	select *
	from groups
	where
		project_id = '-NFNr55R_LYJvxP7wmte'
		and group_id in ('g101', 'g102', 'g103', 'g104', 'g105', 'g106', 'g107', 'g108', 'g109' )
) to 'test_groups.csv' delimiter E'\t' NULL '\N' cs
```

```
\copy (
	select project_id, group_id, task_id, geom, project_type_specifics::json as project_type_specifics from tasks
	where
		project_id = '-NFNr55R_LYJvxP7wmte'
		and group_id in ('g101', 'g102', 'g103', 'g104', 'g105', 'g106', 'g107', 'g108', 'g109' )
) to 'test_tasks.csv' delimiter E'\t' csv
```

These 3 tables contain a column in json format. When exporting this into a csv file there is an issue with the quotes, which prevents us from importing the csv file correctly into the test database. Hence you need to adjust the quotes manually in the csv file.

* open the file with `vi filename.csv`
* type `:` and the first command: `%s/\(.*\t\)"{\(.*\)}"/\1{\2}/g` (capturing groups: \(something\) will save "something" into \1)
* hit enter, then do the same with the second command: `%s/""/"/g` (it's a search/replace expression, like sed, :%s/thing_to_search/repalcement/g)
* save with `:w` for (write) and quit with `:q`

```
\copy (
	select * from mapping_sessions ms
	where project_id = '-NFNr55R_LYJvxP7wmte'
	and group_id in ('g101', 'g102', 'g103', 'g104', 'g105', 'g106', 'g107', 'g108', 'g109' )
) to 'test_mapping_sessions.csv' delimiter E'\t' csv
```

```
\copy (
	select msr.* from mapping_sessions_results msr
	join mapping_sessions ms using (mapping_session_id)
	where
		ms.project_id = '-NFNr55R_LYJvxP7wmte'
		and group_id in ('g101', 'g102', 'g103', 'g104', 'g105', 'g106', 'g107', 'g108', 'g109' )
) to 'test_mapping_sessions_results.csv' delimiter E'\t' csv
```

```
\copy (
	select user_id ,username	,created ,updated_at  from users u
	join mapping_sessions ms using (user_id)
	where
		ms.project_id = '-NFNr55R_LYJvxP7wmte'
		and group_id in ('g101', 'g102', 'g103', 'g104', 'g105', 'g106', 'g107', 'g108', 'g109' )
	group by user_id
) to 'test_users.csv' delimiter E'\t' NULL '\N' csv
```

## Copy files to fixtures
When testing some mapswipe_workers functionality which relies on the postgres DB we use fixtures which are defined in `mapswipe_workers/tests/integration/fixtures`.

Add your files to the right folder concerning the type of your project.
* e.g. add your project file here: `mapswipe_workers/tests/integration/fixtures/tile_map_service_grid/projects/my_project_name.csv`

You can copy the files using scp like this. Make sure to adjust the json quoting issue as described above.

```
scp build_area_sandoa.csv mapswipe-workers-hetzner:/opt/mapswipe/python-mapswipe-workers/test_projects.csv ./tile_map_service_grid/projects
scp build_area_sandoa.csv mapswipe-workers-hetzner:/opt/mapswipe/python-mapswipe-workers/test_groups.csv ./tile_map_service_grid/groups
scp build_area_sandoa.csv mapswipe-workers-hetzner:/opt/mapswipe/python-mapswipe-workers/test_tasks.csv ./tile_map_service_grid/tasks
scp build_area_sandoa.csv mapswipe-workers-hetzner:/opt/mapswipe/python-mapswipe-workers/test_mapping_sessions.csv ./tile_map_service_grid/mapping_sessions
scp build_area_sandoa.csv mapswipe-workers-hetzner:/opt/mapswipe/python-mapswipe-workers/test_mapping_sessions_results.csv ./tile_map_service_grid/mapping_sessions_results
scp build_area_sandoa.csv mapswipe-workers-hetzner:/opt/mapswipe/python-mapswipe-workers/test_users.csv ./tile_map_service_grid/users
```

## Add your test
When adding a new test make sure to set up your postgres DB using your newly created csv files by setting the correct fixture name. In this case all the csv files should be named `build_area_sandoa.csv`.

So for example this file should exist: `mapswipe_workers/tests/integration/fixtures/tile_map_service_grid/projects/build_area_sandoa.csv`

```python
def setUp(self):
	super().setUp()
	project_type = "tile_map_service_grid"
	fixture_name = "build_area_sandoa"
	self.project_id = "-NFNr55R_LYJvxP7wmte"

	for data_type in [
		"projects",
		"groups",
		"tasks",
		"users",
		"mapping_sessions",
		"mapping_sessions_results",
	]:
		set_up.set_postgres_test_data(project_type, data_type, fixture_name)
```

