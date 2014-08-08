import logging

log = logging.getLogger(__name__)


class BoardgameException(Exception):
    """Exception wrapper for Boardgame specific exceptions."""
    pass


class Boardgame(object):
    """ Store information about a boardgame. """

    # __slots__ = [
    #     "designers", "artists", "playingtime", "thumbnail",
    #     "image", "description", "minplayers", "maxplayers",
    #     "categories", "mechanics", "families", "publishers",
    #     "website", "year", "names", "bgid"
    # ]

    def __init__(self, **kwargs):
        self._data = kwargs

        for l in ["designers", "artists", "categories", "mechanics", "families", "publishers", "names"]:
            if l in self._data and type(self._data[l]) != list:
                self._data[l] = [self._data[l]]

    def __getattr__(self, item):
        if item in self._data:
            return self._data[item]
        raise AttributeError

    def __unicode__(self):
        return "{} ({}) (authors: {})".format(self.name, self.year, ", ".join(self.designers))

    def __str__(self):
        return self.__unicode__().encode("utf-8").strip()

    def data(self):
        return self._data

    # Litte syntactic sugar for the more usual case of a single name.
    # @property
    # def name(self):
    #     if getattr(self, "names", None):
    #         return self.names[0]
    #     return None
    #
    # @name.setter
    # def name(self, value):
    #     self.names = [value]
