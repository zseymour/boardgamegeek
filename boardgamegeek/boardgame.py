from .utils import DictObject


class Boardgame(DictObject):

    def __unicode__(self):
        return u"{}".format(self.name)

    def __repr__(self):
        return u"boardgame: {} (id: {})".format(self.name, self.id).encode("utf-8")

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
