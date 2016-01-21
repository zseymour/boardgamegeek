# coding: utf-8
"""
:mod:`boardgamegeek.games` - Games information
==============================================

.. module:: boardgamegeek.games
   :platform: Unix, Windows
   :synopsis: classes for storing games information

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>

"""
from __future__ import unicode_literals
from copy import copy
import datetime

from .things import Thing
from .exceptions import BoardGameGeekError
from .utils import fix_url


class CollectionBoardGame(Thing):
    """
    A boardgame retrieved from the collection information, which has less information than the one retrieved
    via the /thing api and which also contains some user-specific information.
    """

    def __init__(self, data):

        kw = copy(data)
        self._version = None

        if "version" in data:
            version = kw.pop("version")
            print "XXX: version data: {}".format(version)
            self._version = BoardGameVersion(version)

        super(CollectionBoardGame, self).__init__(kw)

    def __repr__(self):
        return "CollectionBoardGame (id: {})".format(self.id)

    def _format(self, log):
        log.info("boardgame id      : {}".format(self.id))
        log.info("boardgame name    : {}".format(self.name))
        log.info("number of plays   : {}".format(self.numplays))
        log.info("last modified     : {}".format(self.lastmodified))
        log.info("rating            : {}".format(self.rating))
        log.info("own               : {}".format(self.owned))
        log.info("preordered        : {}".format(self.preordered))
        log.info("previously owned  : {}".format(self.prev_owned))
        log.info("want              : {}".format(self.want))
        log.info("want to buy       : {}".format(self.want_to_buy))
        log.info("want to play      : {}".format(self.want_to_play))
        log.info("wishlist          : {}".format(self.wishlist))
        log.info("wishlist priority : {}".format(self.wishlist_priority))
        log.info("for trade         : {}".format(self.for_trade))
        if self._version is not None:
            self._version._format(log)

    @property
    def lastmodified(self):
        return self._data.get("lastmodified")

    @property
    def last_modified(self):
        """
        :return: last modified date
        :rtype: str
        """
        return self._data.get("lastmodified")

    @property
    def numplays(self):
        return self._data.get("numplays", 0)

    @property
    def rating(self):
        """
        :return: game rating
        :rtype: float
        :return: ``None`` if n/a
        """
        return self._data.get("rating")

    @property
    def owned(self):
        """
        :return: game owned
        :rtype: bool
        """
        return bool(int(self._data.get("own", 0)))

    @property
    def preordered(self):
        """
        :return: game preordered
        :rtype: bool
        """
        return bool(int(self._data.get("preordered", 0)))

    @property
    def prev_owned(self):
        """
        :return: game previously owned
        :rtype: bool
        """
        return bool(int(self._data.get("prevowned", 0)))

    @property
    def version(self):
        """

        :return: ``None`` if n/a
        :rtype: :pyclass:`boardgamegeek.BoardGameVersion`
        """
        return self._version

    @property
    def want(self):
        """
        :return: game wanted
        :rtype: bool
        """
        return bool(int(self._data.get("want", 0)))

    @property
    def want_to_buy(self):
        """
        :return: want to buy
        :rtype: bool
        """
        return bool(int(self._data.get("wanttobuy", 0)))

    @property
    def want_to_play(self):
        """
        :return: want to play
        :rtype: bool
        """
        return bool(int(self._data.get("wanttoplay", 0)))

    @property
    def for_trade(self):
        """
        :return: game for trading
        :rtype: bool
        """
        return bool(int(self._data.get("fortrade", 0)))

    @property
    def wishlist(self):
        """
        :return: game on wishlist
        :rtype: bool
        """
        return bool(int(self._data.get("wishlist", 0)))

    @property
    def wishlist_priority(self):
        # TODO: convert to int (it's str)
        return self._data.get("wishlistpriority")


class BoardGameVideo(Thing):
    """
    Object containing information about a board game video
    """
    def __init__(self, data):
        kw = copy(data)

        if "post_date" in kw:
            date = kw["post_date"]
            if type(date) != datetime.datetime:
                try:
                    kw["date"] = datetime.datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S")
                except:
                    kw["date"] = None

        super(BoardGameVideo, self).__init__(kw)

    @property
    def category(self):
        """
        :return: the category of this video
        :return: ``None`` if n/a
        :rtype: string
        """
        return self._data.get("category")

    @property
    def link(self):
        """
        :return: the link to this video
        :return: ``None`` if n/a
        :rtype: string
        """
        return self._data.get("link")

    @property
    def language(self):
        """
        :return: the language of this video
        :return: ``None`` if n/a
        :rtype: string
        """
        return self._data.get("language")

    @property
    def uploader(self):
        """
        :return: the name of the user which uploaded this video
        :return: ``None`` if n/a
        :rtype: string
        """
        return self._data.get("uploader")

    @property
    def uploader_id(self):
        """
        :return: id of the uploader
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("uploader_id")

    @property
    def post_date(self):
        """
        :return: date when this video was uploaded
        :rtype: datetime.datetime
        :return: ``None`` if n/a
        """
        return self._data.get("post_date")


class BoardGameVersion(Thing):
    """
    Object containing information about a board game version
    """
    def __init__(self, data):
        kw = copy(data)

        for to_fix in ["thumbnail", "image"]:
            if to_fix in kw:
                kw[to_fix] = fix_url(kw[to_fix])

        super(BoardGameVersion, self).__init__(kw)

    def __repr__(self):
        return "BoardGameVersion (id: {})".format(self.id)

    def _format(self, log):
        log.info("version id        : {}".format(self.id))
        log.info("version name      : {}".format(self.name))
        log.info("version language  : {}".format(self.language))
        log.info("version publisher : {}".format(self.publisher))
        log.info("version artist    : {}".format(self.artist))
        log.info("W x L x D         : {} x {} x {}".format(self.width, self.length, self.depth))
        log.info("weight            : {}".format(self.weight))
        log.info("year              : {}".format(self.year))

    @property
    def artist(self):
        """

        :return: artist of this version
        :rtype: string
        :return: ``None`` if n/a
        """
        return self._data.get("artist")

    @property
    def depth(self):
        """
        :return: depth of the box
        :rtype: double
        :return: 0.0 if n/a
        """
        return self._data.get("depth")

    @property
    def length(self):
        """
        :return: length of the box
        :rtype: double
        :return: 0.0 if n/a
        """
        return self._data.get("length")

    @property
    def language(self):
        """
        :return: language of this version
        :rtype: string
        :return: ``None`` if n/a
        """
        return self._data.get("language")

    @property
    def name(self):
        """
        :return: name of this version
        :rtype: string
        :return: ``None`` if n/a
        """
        return self._data.get("name")

    @property
    def publisher(self):
        """

        :return: publisher of this version
        :rtype: string
        :return: ``None`` if n/a
        """
        return self._data.get("publisher")

    @property
    def weight(self):
        """
        :return: weight of the box
        :rtype: double
        :return: 0.0 if n/a
        """
        return self._data.get("weight")

    @property
    def width(self):
        """
        :return: width of the box
        :rtype: double
        :return: 0.0 if n/a
        """
        return self._data.get("width")

    @property
    def year(self):
        """
        :return: publishing year
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("yearpublished")



class BoardGame(Thing):
    """
    Object containing information about a board game
    """
    def __init__(self, data):

        kw = copy(data)

        # Fix thumbnail/image links
        for to_fix in ["thumbnail", "image"]:
            if to_fix in kw:
                kw[to_fix] = fix_url(kw[to_fix])

        # if we have any "expansions" for this item..
        if "expansions" not in kw:
            kw["expansions"] = []

        self._expansions = []           # list of Thing for the expansions
        self._expansions_set = set()    # set for making sure things are unique
        for data in kw["expansions"]:
            try:
                if data["id"] not in self._expansions_set:
                    self._expansions_set.add(data["id"])
                    self._expansions.append(Thing(data))
            except KeyError:
                raise BoardGameGeekError("invalid expansion data")

        # if this item expands something...
        if "expands" not in kw:
            kw["expands"] = []

        self._expands = []              # list of Thing which this item expands
        self._expands_set = set()       # set for keeping things unique
        for data in kw["expands"]:         # for all the items this game expands, create a Thing
            try:
                if data["id"] not in self._expands_set:
                    self._expands_set.add(data["id"])
                    self._expands.append(Thing(data))
            except KeyError:
                raise BoardGameGeekError("invalid expanded game data")

        if "videos" not in kw:
            kw["videos"] = []

        self._videos = []
        self._videos_ids = set()
        for video in kw["videos"]:
            try:
                if video["id"] not in self._videos_ids:
                    self._videos.append(BoardGameVideo(video))
                    self._videos_ids.add(video["id"])
            except KeyError:
                raise BoardGameGeekError("invalid video data")

        self.boardgame_rank = None

        if "ranks" in kw:
            # try to search for the boardgame rank of this game
            for rank in kw["ranks"]:
                if rank.get("name") == "boardgame":
                    value = rank.get("value")
                    if value is None:
                        self.boardgame_rank = None
                    else:
                        self.boardgame_rank = int(value)
                    break

        super(BoardGame, self).__init__(kw)

    def __repr__(self):
        return "BoardGame (id: {})".format(self.id)

    def add_expanded_game(self, data):
        """
        Add a game expanded by this one

        :param dict data: expanded game's data
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekError` if data is invalid
        """
        try:
            if data["id"] not in self._expands_set:
                self._data["expands"].append(data)
                self._expands_set.add(data["id"])
                self._expands.append(Thing(data))
        except KeyError:
            raise BoardGameGeekError("invalid expanded game data")

    def add_expansion(self, data):
        """
        Add an expansion of this game

        :param dict data: expansion data
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekError` if data is invalid
        """
        try:
            if data["id"] not in self._expansions_set:
                self._data["expansions"].append(data)
                self._expansions_set.add(data["id"])
                self._expansions.append(Thing(data))
        except KeyError:
            raise BoardGameGeekError("invalid expansion data")

    def _format(self, log):
        log.info("boardgame id      : {}".format(self.id))
        log.info("boardgame name    : {}".format(self.name))
        log.info("boardgame rank    : {}".format(self.boardgame_rank))
        if self.alternative_names:
            for i in self.alternative_names:
                log.info("alternative name  : {}".format(i))
        log.info("year published    : {}".format(self.year))
        log.info("minimum players   : {}".format(self.min_players))
        log.info("maximum players   : {}".format(self.max_players))
        log.info("playing time      : {}".format(self.playing_time))
        log.info("minimum age       : {}".format(self.min_age))
        log.info("thumbnail         : {}".format(self.thumbnail))
        log.info("image             : {}".format(self.image))

        log.info("is expansion      : {}".format(self.expansion))

        if self.expansions:
            log.info("expansions")
            for i in self.expansions:
                log.info("- {}".format(i.name))

        if self.expands:
            log.info("expands")
            for i in self.expands:
                log.info("- {}".format(i.name))

        if self.categories:
            log.info("categories")
            for i in self.categories:
                log.info("- {}".format(i))

        if self.families:
            log.info("families")
            for i in self.families:
                log.info("- {}".format(i))

        if self.mechanics:
            log.info("mechanics")
            for i in self.mechanics:
                log.info("- {}".format(i))

        if self.implementations:
            log.info("implementations")
            for i in self.implementations:
                log.info("- {}".format(i))

        if self.designers:
            log.info("designers")
            for i in self.designers:
                log.info("- {}".format(i))

        if self.artists:
            log.info("artistis")
            for i in self.artists:
                log.info("- {}".format(i))

        if self.publishers:
            log.info("publishers")
            for i in self.publishers:
                log.info("- {}".format(i))

        log.info("users rated game  : {}".format(self.users_rated))
        log.info("users avg rating  : {}".format(self.rating_average))
        log.info("users b-avg rating: {}".format(self.rating_bayes_average))
        log.info("users commented   : {}".format(self.users_commented))
        log.info("users owned       : {}".format(self.users_owned))
        log.info("users wanting     : {}".format(self.users_wanting))
        log.info("users wishing     : {}".format(self.users_wishing))
        log.info("users trading     : {}".format(self.users_trading))
        log.info("ranks             : {}".format(self.ranks))
        log.info("description       : {}".format(self.description))

    @property
    def alternative_names(self):
        """
        :return: alternative names
        :rtype: list of str
        """
        return self._data.get("alternative_names", [])

    @property
    def thumbnail(self):
        """
        :return: thumbnail URL
        :rtype: str
        :return: ``None`` if n/a
        """
        return self._data.get("thumbnail")

    @property
    def image(self):
        """
        :return: image URL
        :rtype: str
        :return: ``None`` if n/a
        """
        return self._data.get("image")

    @property
    def description(self):
        """
        :return: description
        :rtype: str
        """
        return self._data.get("description", "")

    @property
    def families(self):
        """
        :return: families
        :rtype: list of str
        """
        return self._data.get("families", [])

    @property
    def categories(self):
        """
        :return: categories
        :rtype: list of str
        """
        return self._data.get("categories", [])

    @property
    def mechanics(self):
        """
        :return: mechanics
        :rtype: list of str
        """
        return self._data.get("mechanics", [])

    @property
    def expansions(self):
        """
        :return: expansions
        :rtype: list of :py:class:`boardgamegeek.things.Thing`
        """
        return self._expansions

    @property
    def expands(self):
        """
        :return: games this item expands
        :rtype: list of :py:class:`boardgamegeek.things.Thing`
        """
        return self._expands

    @property
    def implementations(self):
        """
        :return: implementations
        :rtype: list of str
        """
        return self._data.get("implementations", [])

    @property
    def designers(self):
        """
        :return: designers
        :rtype: list of str
        """
        return self._data.get("designers", [])

    @property
    def artists(self):
        """
        :return: artists
        :rtype: list of str
        """
        return self._data.get("artists", [])

    @property
    def publishers(self):
        """
        :return: publishers
        :rtype: list of str
        """
        return self._data.get("publishers", [])

    @property
    def expansion(self):
        """
        :return: True if this item is an expansion
        :rtype: bool
        """
        return self._data.get("expansion", False)

    @property
    def year(self):
        """
        :return: publishing year
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("yearpublished")

    @property
    def min_players(self):
        """
        :return: minimum number of players
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("minplayers")

    @property
    def max_players(self):
        """
        :return: maximum number of players
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("maxplayers")

    @property
    def playing_time(self):
        """
        :return: playing time
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("playingtime")

    @property
    def min_playing_time(self):
        """
        Minimum playing time
        :return: ``None if n/a
        :rtype: integer
        """
        return self._data.get("minplaytime")

    @property
    def max_playing_time(self):
        """
        Maximum playing time
        :return: ``None if n/a
        :rtype: integer
        """
        return self._data.get("maxplaytime")

    @property
    def min_age(self):
        """
        :return: minimum recommended age
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("minage")

    @property
    def users_rated(self):
        """
        :return: how many users rated the game
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("usersrated")

    @property
    def rating_average(self):
        """
        :return: average rating
        :rtype: float
        :return: ``None`` if n/a
        """
        return self._data.get("average")

    @property
    def rating_bayes_average(self):
        """
        :return: bayes average rating
        :rtype: float
        :return: ``None`` if n/a
        """
        return self._data.get("bayesaverage")

    @property
    def rating_stddev(self):
        """
        :return: standard deviation
        :rtype: float
        :return: ``None`` if n/a
        """
        return self._data.get("stddev")

    @property
    def rating_median(self):
        """
        :return:
        :rtype: float
        :return: ``None`` if n/a
        """
        return self._data.get("median")

    @property
    def users_owned(self):
        """
        :return: number of users owning this game
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("owned")

    @property
    def users_trading(self):
        """
        :return: number of users trading this game
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("trading")

    @property
    def users_wanting(self):
        """
        :return: number of users wanting this game
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("wanting")

    @property
    def users_wishing(self):
        """
        :return: number of users wishing for this game
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("wishing")

    @property
    def users_commented(self):
        """
        :return: number of user comments
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("numcomments")

    @property
    def rating_num_weights(self):
        """
        :return:
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("numweights")

    @property
    def rating_average_weight(self):
        """
        :return: average weight
        :rtype: float
        :return: ``None`` if n/a
        """
        return self._data.get("averageweight")

    @property
    def ranks(self):
        """
        :return: rankings of this game
        :rtype: list of dicts, keys: ``friendlyname`` (the friendly name of the rank, e.g. "Board Game Rank"), ``name``
                (name of the rank, e.g "boardgame"), ``value`` (the rank)
        :return: ``None`` if n/a
        """
        return self._data.get("ranks")
