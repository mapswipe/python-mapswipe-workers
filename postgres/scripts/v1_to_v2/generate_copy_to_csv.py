import sys


def get_query(project_ids):
    clause = ("WHERE project_id in (select project_id from results group by "
              "project_id)")
    clause_import = ("WHERE import_id in (select importkey as import_id from "
                     "projects)")
    clause_group = ("WHERE project_id in (select project_id from projects "
                    "group by project_id) and project_id in (select "
                    "project_id from results group by project_id)")
    if project_ids is None:
        pass
    elif len(project_ids) == 1:
        clause = f"{clause} AND project_id = {project_ids[0]}"
        clause_import = (f", projects p {clause_import} AND p.project_id = "
                         f"{project_ids[0]} AND p.importkey = i.import_id")
        clause_group = f"{clause_group} AND project_id = {project_ids[0]}"
    else:
        clause = f"{clause} AND project_id = {project_ids[0]}"
        clause_group = f"{clause_group} AND project_id = {project_ids[0]}"
        clause_import = (f", projects p {clause_import} AND p.project_id = "
                         f"{project_ids[0]} AND p.importkey = i.import_id")
        for project_id in project_ids[1:]:
            clause = clause + f" OR project_id = {project_id}"
            clause_group = clause_group + f" OR project_id = {project_id}"
            clause_import = (f"{clause} OR p.project_id={project_id} AND "
                             f"p.importkey=i.import_id")

    query = (
        f"-- Export v1 MapSwipe data to csv.\n"
        f"-- Rename attributes to conform to v2.\n"
        f'\\copy (SELECT archive, image, importkey as "import_id", isfeatured '
        f'AS "is_featured", lookfor AS "look_for", name, progress,'
        f'projectdetails AS "project_details", project_id, project_type, state'
        f'AS "status", info AS "project_type_specifics" FROM projects '
        f'{clause}) TO projects.csv WITH (FORMAT CSV, DELIMITER ",", '
        f'HEADER TRUE);\n'
        f'\\copy (SELECT i.import_id, i.info FROM imports i {clause_import}) '
        f'TO imports.csv WITH (FORMAT CSV, DELIMITER ",", HEADER TRUE);\n'
        f'\\copy (SELECT project_id, group_id as "v1_group_id", count as '
        f'"number_of_tasks", completedcount as "finished_count", '
        f'verificationcount as "required_count", info as '
        f'"project_type_specifics" FROM groups {clause_group} ) TO groups.csv'
        f' WITH (FORMAT CSV, DELIMITER ",", HEADER TRUE);\n'
        f'\\copy (SELECT project_id, group_id as "v1_group_id", task_id, info '
        f'as "project_type_specifics" FROM tasks {clause_group} LIMIT '
        f'10000000) TO tasks1.csv WITH (FORMAT CSV, DELIMITER ",", '
        f'HEADER TRUE);\n'
        f'\\copy (SELECT project_id, group_id as "v1_group_id", task_id, info '
        f'as "project_type_specifics" FROM tasks {clause_group} OFFSET '
        f'10000000 LIMIT 10000000) TO tasks2.csv WITH (FORMAT CSV, DELIMITER '
        f'",", HEADER TRUE);\n'
        f'\\copy (SELECT project_id, group_id as "v1_group_id", task_id, info '
        f'as "project_type_specifics" FROM tasks {clause_group} OFFSET '
        f'20000000 LIMIT 10000000) TO tasks3.csv WITH (FORMAT CSV, DELIMITER '
        f'",", HEADER TRUE);\n'
        f'\\copy (SELECT project_id, group_id as "v1_group_id", task_id, info '
        f'as "project_type_specifics" FROM tasks {clause_group} OFFSET '
        f'30000000) TO tasks4.csv WITH (FORMAT CSV, DELIMITER '
        f'",", HEADER TRUE);\n'
        f'\\copy (SELECT user_id, username FROM users) TO users.csv WITH '
        f'(FORMAT CSV, DELIMITER ",", HEADER TRUE);\n'
    )
    return query


def get_result_query(project_ids):
    clause = ("WHERE project_id in (SELECT project_id FROM projects GROUP BY "
              "project_id) AND user_id in (SELECT user_id FROM users)")
    if project_ids is None:
        pass
    elif len(project_ids) == 1:
        clause = f"{clause} AND project_id = {project_ids[0]}"
    else:
        clause = f"{clause} AND project_id = {project_ids[0]}"
        for project_id in project_ids[1:]:
            clause = clause + f" OR project_id = {project_id}"

    query = (
        f"-- Export v1 MapSwipe data to csv.\n"
        f"-- Rename attributes to conform to v2.\n"
        f'\\copy (SELECT project_id, task_id, user_id, timestamp as "timeint",'
        f' info FROM results {clause}) TO results.csv WITH (FORMAT CSV,'
        f' DELIMITER ",", HEADER TRUE);\n'
    )
    return query


if __name__ == "__main__":
    if len(sys.argv) == 1:
        query = get_query(None)
        result_query = get_result_query(None)
    else:
        query = get_query(sys.argv[1:])
        result_query = get_result_query(sys.argv[1:])

    with open("copy_to_csv.sql", "w") as f:
        f.write(query)

    with open("copy_results_to_csv.sql", "w") as f:
        f.write(result_query)
