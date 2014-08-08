from .utils import DictObject


class Boardgame(DictObject):

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
        return self._data.get("max_players")

    @property
    def playing_time(self):
        return self._data.get("playingtime")

    @property
    def min_age(self):
        return self._data.get("minage")
