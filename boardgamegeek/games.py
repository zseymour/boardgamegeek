from .utils import DictObject


class CollectionBoardGame(DictObject):
    """
    A boardgame retrieved from the collection information, which has
    less information than the one retrieved via the /thing api and which
    also contains some user-specific information
    """

    def __unicode__(self):
        return u"{}".format(self.name)

    def __repr__(self):
        return u"boardgame: {} (id: {})".format(self.name, self.id).encode("utf-8")

    def _format(self, log):
        log.info(u"boardgame id      : {}".format(self.id))
        log.info(u"boardgame name    : {}".format(self.name))

        log.info(u"last modified     : {}".format(self.lastmodified))

        log.info(u"rating            : {}".format(self.rating))
        log.info(u"own               : {}".format(self.owned))
        log.info(u"preordered        : {}".format(self.preordered))
        log.info(u"previously owned  : {}".format(self.prev_owned))
        log.info(u"want              : {}".format(self.want))
        log.info(u"want to buy       : {}".format(self.want_to_buy))
        log.info(u"want to play      : {}".format(self.want_to_play))
        log.info(u"wishlist          : {}".format(self.wishlist))
        log.info(u"wishlist priority : {}".format(self.wishlist_priority))
        log.info(u"for trade         : {}".format(self.for_trade))

    @property
    def lastmodified(self):
        return self._data.get("lastmodified")

    @property
    def name(self):
        return self._data.get("name")

    @property
    def id(self):
        return self._data.get("id")

    @property
    def rating(self):
        return self._data.get("rating")

    @property
    def owned(self):
        return bool(int(self._data.get("own", 0)))

    @property
    def preordered(self):
        return bool(int(self._data.get("preordered", 0)))

    @property
    def prev_owned(self):
        return bool(int(self._data.get("prevowned", 0)))

    @property
    def want(self):
        return bool(int(self._data.get("want", 0)))

    @property
    def want_to_buy(self):
        return bool(int(self._data.get("wanttobuy", 0)))

    @property
    def want_to_play(self):
        return bool(int(self._data.get("wanttoplay", 0)))

    @property
    def for_trade(self):
        return bool(int(self._data.get("fortrade", 0)))

    @property
    def wishlist(self):
        return bool(int(self._data.get("wishlist", 0)))

    @property
    def wishlist_priority(self):
        return (self._data.get("wishlistpriority"))


class BoardGame(DictObject):

    def __unicode__(self):
        return u"{}".format(self.name)

    def __repr__(self):
        return u"boardgame: {} (id: {})".format(self.name, self.id).encode("utf-8")

    def _format(self, log):
        log.info(u"boardgame id      : {}".format(self.id))
        log.info(u"boardgame name    : {}".format(self.name))
        if self.alternative_names:
            for i in self.alternative_names:
                log.info(u"alternative name  : {}".format(i))
        log.info(u"publishing year   : {}".format(self.year))
        log.info(u"minimum players   : {}".format(self.min_players))
        log.info(u"maximum players   : {}".format(self.max_players))
        log.info(u"playing time      : {}".format(self.playing_time))
        log.info(u"minimum age       : {}".format(self.min_age))
        log.info(u"thumbnail         : {}".format(self.thumbnail))
        log.info(u"image             : {}".format(self.image))

        if self.expansions:
            log.info("expansions")
            for i in self.expansions:
                log.info(u"- {}".format(i))

        if self.categories:
            log.info("categories")
            for i in self.categories:
                log.info(u"- {}".format(i))

        if self.families:
            log.info("families")
            for i in self.families:
                log.info(u"- {}".format(i))

        if self.mechanics:
            log.info("mechanics")
            for i in self.mechanics:
                log.info(u"- {}".format(i))

        if self.implementations:
            log.info("implementations")
            for i in self.implementations:
                log.info(u"- {}".format(i))

        if self.designers:
            log.info("designers")
            for i in self.designers:
                log.info(u"- {}".format(i))

        if self.artists:
            log.info("artistis")
            for i in self.artists:
                log.info(u"- {}".format(i))

        if self.publishers:
            log.info("publishers")
            for i in self.publishers:
                log.info(u"- {}".format(i))

        log.info(u"users rated game  : {}".format(self.users_rated))
        log.info(u"users avg rating  : {}".format(self.rating_average))
        log.info(u"users b-avg rating: {}".format(self.rating_bayes_average))
        log.info(u"users commented   : {}".format(self.users_commented))
        log.info(u"users owned       : {}".format(self.users_owned))
        log.info(u"users wanting     : {}".format(self.users_wanting))
        log.info(u"users wishing     : {}".format(self.users_wishing))
        log.info(u"users trading     : {}".format(self.users_trading))
        log.info(u"ranks             : {}".format(self.ranks))
        log.info(u"description       : {}".format(self.description))

    @property
    def name(self):
        return self._data.get("name")

    @property
    def alternative_names(self):
        return self._data.get("alternative_names")

    @property
    def id(self):
        return self._data.get("id")

    @property
    def thumbnail(self):
        return self._data.get("thumbnail")

    @property
    def image(self):
        return self._data.get("image")

    @property
    def description(self):
        return self._data.get("description")

    @property
    def families(self):
        return self._data.get("families")

    @property
    def categories(self):
        return self._data.get("categories")

    @property
    def mechanics(self):
        return self._data.get("mechanics")

    @property
    def expansions(self):
        return self._data.get("expansions")

    @property
    def implementations(self):
        return self._data.get("implementations")

    @property
    def designers(self):
        return self._data.get("designers")

    @property
    def artists(self):
        return self._data.get("artists")

    @property
    def publishers(self):
        return self._data.get("publishers")

    @property
    def year(self):
        return self._data.get("yearpublished")

    @property
    def min_players(self):
        return self._data.get("minplayers")

    @property
    def max_players(self):
        return self._data.get("maxplayers")

    @property
    def playing_time(self):
        return self._data.get("playingtime")

    @property
    def min_age(self):
        return self._data.get("minage")

    @property
    def users_rated(self):
        return self._data.get("usersrated")

    @property
    def rating_average(self):
        return self._data.get("average")

    @property
    def rating_bayes_average(self):
        return self._data.get("bayesaverage")

    @property
    def rating_stddev(self):
        return self._data.get("stddev")

    @property
    def rating_median(self):
        return self._data.get("median")

    @property
    def users_owned(self):
        return self._data.get("owned")

    @property
    def users_trading(self):
        return self._data.get("trading")

    @property
    def users_wanting(self):
        return self._data.get("wanting")

    @property
    def users_wishing(self):
        return self._data.get("wishing")

    @property
    def users_commented(self):
        return self._data.get("numcomments")

    @property
    def rating_num_weights(self):
        return self._data.get("numweights")

    @property
    def rating_average_weight(self):
        return self._data.get("averageweight")

    @property
    def ranks(self):
        return self._data.get("ranks")