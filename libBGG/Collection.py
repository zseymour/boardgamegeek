import logging

log = logging.getLogger(__name__)


class CollectionException(Exception):
    """Exception wrapper for Collection specific exceptions."""
    pass


class Rating(object):
    #__slots__ = ["name", "bgid", "userrating", "usersrated", "average", "stddev",
    #             "bayesaverage", "BGGrank", "median"]

    def __init__(self, **kwargs):
        self._data = kwargs

    def __getattr__(self, item):
        # allow accessing user's variables using .attribute
        if item in self._data:
            return self._data[item]
        raise AttributeError


class BoardgameStatus(object):
    #__slots__ = ["name", "bgid", "own", "prevown", "fortrade", "want", "wanttoplay",
    #             "wanttobuy", "wishlist", "wishlistpriority", "timestamp", "numplays"]

    def __init__(self, **kwargs):
        self._data = kwargs

    def __getattr__(self, item):
        # allow accessing user's variables using .attribute
        if item in self._data:
            return self._data[item]
        raise AttributeError


class Collection(object):
    """
    Store information about a Collection. The init function takes a list of valid
    proprties defined by Collection.valid_properties. Properties that are lists can
    be given as a single item or as a list.

    The Collection class contains a list of minimally filled out Boardgames as
    well as a rating map for those games. Each rating contains # users rated, 
    average, stddev, median, BGG Boardgame rank, etc as well as the User"s rating if given.

    Ratings are mapped by boardgame name.
    """
    def __init__(self, username):

        self.username = username
        self.games = list()
        self.rating = dict()   # index is BG name
        self.status = dict()   # index is BG name

    def __unicode__(self):
        return "{}'s collection, {} items".format(self.username, len(self.games))

    def __str__(self):
        return self.__unicode__().encode("utf-8").strip()

    def data(self):
        return {"user": self.username,
                "games": [game.data() for game in self.games]}

    def add_boardgame(self, boardgame):
        self.games.append(boardgame)

    def add_boardgame_status(self, name, status):
        """

        :param name: The name of the boardgame
        :param status:
        :return:
        """
        self.status[name] = status

    def add_boardgame_rating(self, name, rating):
        """

        :param name:
        :param rating:
        :return:
        """
        self.rating[name] = rating

    def __len__(self):
        return len(self.games)
