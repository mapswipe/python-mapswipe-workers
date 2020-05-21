from abc import ABCMeta, abstractmethod
from mapswipe_workers import auth


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
