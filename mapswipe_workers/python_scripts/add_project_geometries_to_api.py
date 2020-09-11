from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers import auth
from mapswipe_workers.utils import geojson_functions
import ogr


def add_project_geometries_to_api():
    """Load project geometries from postgres and save as geojson."""

    # load from postgres
    pg_db = auth.postgresDB()
    sql_query = """
        SELECT
            project_id
            ,ST_AsText(geom) as geom
        FROM projects
        """
    data = pg_db.retr_query(sql_query)
    print(len(data))

    # save as geojson one by one
    for project in data:
        project_id = project[0]
        wkt_geom = project[1]

        outfile = (
            f"{DATA_PATH}/api/project_geometries/project_geom_{project_id}"
            f".geojson"
        )
        try:
            geometries = [ogr.CreateGeometryFromWkt(wkt_geom)]
            geojson_functions.create_geojson_file(geometries, outfile)
        except Exception:
            print(f"got an error for {project_id}")
            # just ignore if this fails
            pass


add_project_geometries_to_api()
