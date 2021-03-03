from abc import ABCMeta

from mapswipe_workers import auth
from mapswipe_workers.definitions import CustomError


class BaseTileServer(metaclass=ABCMeta):
    """Create a tile server class."""

    def __init__(self, tile_server_dict):

        self.name = tile_server_dict.get("name", "bing")

        # set base url
        self.url = tile_server_dict.get(
            "url", auth.get_tileserver_url(tile_server_dict.get("name", "bing"))
        )
        if self.url == "":
            self.url = auth.get_tileserver_url(tile_server_dict.get("name", "bing"))

        # check if url contains the right place holders
        if not self.check_imagery_url():
            raise CustomError(
                f"The imagery url '{self.url}' must contain {x}, {y} and {z} or "
                "the {quad_key} placeholders."
            )

        # set api key
        self.apiKey = tile_server_dict.get(
            "apiKey", auth.get_api_key(tile_server_dict.get("name", "bing"))
        )
        if self.apiKey == "":
            self.apiKey = auth.get_api_key(tile_server_dict.get("name", "bing"))

        # only needed if tile server is a WMS
        self.wmtsLayerName = tile_server_dict.get("wmtsLayerName", None)
        if self.wmtsLayerName == "":
            self.wmtsLayerName = None

        self.credits = tile_server_dict.get("credits", "")

        # currently not used in client and project creation
        self.captions = tile_server_dict.get("caption", None)
        self.date = tile_server_dict.get("date", None)

    def check_imagery_url(self):
        """Check if imagery url contains xyz or quad key placeholders."""
        if all([substring in self.url for substring in ["{x}", "{y}", "{z}"]]):
            return True
        elif "{quad_key}" in self.url:
            return True
        else:
            return False

