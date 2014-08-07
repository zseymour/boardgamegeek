import logging


log = logging.getLogger(__name__)


class UserException(Exception):
    """Exception wrapper for User specific exceptions."""
    pass


class User(object):
    """ Store information about a BGG User. """

    # This should really contain the correct types as well...
    # __slots__ = [
    #     "name", "hot10", "top10", "firstname", "lastname", "yearregistered", "lastlogin",
    #     "stateorprovince", "country", "traderating", "bgid"
    # ]
    def __init__(self, **kwargs):

        self._data = kwargs

        for l in ["top10", "hot10"]:
            if l in self._data and type(self._data[l]) != list:
                self._data[l] = [self._data[l]]

    def __getattr__(self, item):
        # allow accessing user's variables using .attribute
        if item in self._data:
            return self._data[item]
        raise AttributeError

    def __unicode__(self):
        return "{} {}".format(self.firstname, self.lastname)

    def __str__(self):
        return self.__unicode__().encode("utf-8").strip()

    def data(self):
        # useful for serialization as JSON
        return self._data

    @property
    def fullname(self):
        return " ".join([self.firstname, self.lastname]).encode("utf-8").strip()
