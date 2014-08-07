import logging

log = logging.getLogger(__name__)


class GuildException(Exception):
    """Exception wrapper for Guild specific exceptions."""
    pass


class Guild(object):
    """ Store information about a BGG Guild. The init function takes a list of valid
    proprties defined by Guild.valid_properties. """

    # __slots__ = [
    #     "category", "website", "manager", "description", "members", "name", "gid"
    # ]

    def __init__(self, **kwargs):
        self._data = kwargs
        if "members" in self._data and type(self._data["members"]) != list:
            self._data["members"] = [self._data["members"]]

    def __getattr__(self, item):
        # allow accessing user's variables using .attribute
        if item in self._data:
            return self._data[item]
        raise AttributeError

    def data(self):
        # useful for serialization as JSON
        return self._data

    def __unicode__(self):
        return "Guild {} (id={})".format(self.name, self.gid)

    def __str__(self):
        return self.__unicode__().encode("utf-8").strip()
