from __future__ import unicode_literals
from copy import copy
from .utils import DictObject


class PlaySession(DictObject):

    def _format(self, log):
        log.info("play id         : {}".format(self.id))
        log.info("play user id    : {}".format(self.user_id))
        log.info("play date       : {}".format(self.date.strftime("%Y-%m-%d")))
        log.info("play quantity   : {}".format(self.quantity))
        log.info("play duration   : {}".format(self.duration))
        log.info("play incomplete : {}".format(self.incomplete))
        log.info("play nowinstats : {}".format(self.nowinstats))
        log.info("play game       : {} ({})".format(self.game_name, self.game_id))
        log.info("play comment    : {}".format(self.comment))

    @property
    def id(self):
        return self._data.get("id")

    @property
    def user_id(self):
        return self._data.get("userid")

    @property
    def date(self):
        return self._data.get("date")

    @property
    def quantity(self):
        return self._data.get("quantity")

    @property
    def duration(self):
        return self._data.get("duration")

    @property
    def incomplete(self):
        return self._data.get("incomplete")

    @property
    def nowinstats(self):
        return self._data.get("nowinstats")

    @property
    def game_id(self):
        return self._data.get("game_id")

    @property
    def game_name(self):
        return self._data.get("game_name")

    @property
    def comment(self):
        return self._data.get("comment")


class Plays(DictObject):

    def __init__(self, data):
        kw = copy(data)
        if "plays" not in kw:
            kw["plays"] = []
        self._plays = []
        super(Plays, self).__init__(kw)

    def _format(self, log):
        if self.user:
            log.info("plays of        : {} ({})".format(self.user, self.user_id))
        else:
            log.info("plays of game id: {}".format(self.game_id))
        log.info("count           : {}".format(len(self)))
        for p in self.plays:
            p._format(log)
            log.info("-------------")

    def __len__(self):
        return len(self._plays)

    def _add_play(self, data):
        self._data["plays"].append(data)
        self._plays.append(PlaySession(data))

    @property
    def user(self):
        return self._data.get("username")

    @property
    def user_id(self):
        return self._data.get("user_id")

    @property
    def game_id(self):
        return self._data.get("game_id")

    @property
    def plays(self):
        return self._plays