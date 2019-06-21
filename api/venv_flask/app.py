from flask import Flask
from config import app_config
from bbox import BBox2D
from flask import jsonify
from shapely.geometry.polygon import Polygon

from planar import BoundingBox


import json

def create_app(env_name):
    """
    Create app
    """

    # app initiliazation
    app = Flask(__name__)

    app.config.from_object(app_config[env_name])

    @app.route('/projects', methods=['GET'])
    def get_projects():
        data = []
        fin_proj = "data/fin_projects_stats.json"
        with open(fin_proj) as f:
            for line in f:
                data.append(json.loads(line))
        return jsonify(data)

    @app.route('/projects/<int:project_id>', methods=['GET'])
    def get_projects_by_id(project_id):
        res_data = []
        fin_proj = "data/fin_projects_stats.json"
        with open(fin_proj) as f:
            for line in f:
                y = json.loads(line)
                if y['project_id'] == project_id:
                    res_data.append(json.loads(line))
        return jsonify(res_data)

#yest to be done
    # @app.route('/boundingbox', methods=['GET'])
    # def get_bounding_box():
    #     res_data = []
    #     fin_proj = "data/projects_extents.geojson"
    #     bounding_box = BoundingBox([(-71.17768203,42.39037017), (-71.00,42.00), (-71.1203,42.3017), (-70.17768203,42.317)])
    #     with open(fin_proj) as f:
    #         data = json.load(f)
    #     # return  jsonify(data['features'][0]['geometry']['coordinates'][0])
    #
    #     # feature = data['features'][0]
    #     for feature in data['features']:
    #         polygon = feature['geometry']
    #         if polygon is not None and len(polygon['coordinates'])!= 0 :
    #             for coordinate in polygon['coordinates'][0]:
    #                 if coordinate is not None and type(coordinate[0]) == int:
    #                     if bounding_box.contains_point(coordinate):
    #                         res_data.append(coordinate)
    #                 elif coordinate is not None:
    #                     for c in coordinate:
    #                         if type(c) == list and bounding_box.contains_point(c):
    #                             res_data.append(c)
    #
    #     return jsonify(res_data)

    return app
