import unittest

from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.definitions import CustomError


class TestCheckImageryUrl(unittest.TestCase):
    def test_correct_xyz_placeholders(self):
        tile_server_dict = {
            "name": "custom",
            "credits": "custom imagery provider",
            "url": "https://mytms.com/{x}/{y}/{z}.png"
        }
        tile_server = BaseTileServer(tile_server_dict)

    def test_correct_quadkey_placeholders(self):
        tile_server_dict = {
            "name": "custom",
            "credits": "custom imagery provider",
            "url": "https://mytms.com/{quad_key}.png"
        }
        tile_server = BaseTileServer(tile_server_dict)

    def test_wrong_xyz_placeholders(self):
        tile_server_dict = {
            "name": "custom",
            "credits": "custom imagery provider",
            "url": "https://mytms.com/{x}/{y}/{zoom}.png"
        }
        self.assertRaises(CustomError, BaseTileServer, tile_server_dict)

    def test_wrong_quadkey_placeholders(self):
        tile_server_dict = {
            "name": "custom",
            "credits": "custom imagery provider",
            "url": "https://mytms.com/{quadkey}.png"
        }
        self.assertRaises(CustomError, BaseTileServer, tile_server_dict)


if __name__ == "__main__":
    unittest.main()
