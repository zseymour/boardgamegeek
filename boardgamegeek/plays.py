# coding: utf-8
"""
:mod:`boardgamegeek.plays` - BoardGameGeek "Plays"
==================================================

.. module:: boardgamegeek.plays
   :platform: Unix, Windows
   :synopsis: BGG "Plays"

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>

"""
from __future__ import unicode_literals
from copy import copy
import datetime

from .exceptions import BoardGameGeekError
from .utils import DictObject


class PlaySession(DictObject):
    """
    Container for a play session information.
    """

    def __init__(self, data):
        if "id" not in data:
            raise BoardGameGeekError("missing id of PlaySession")

        if "date" in data:
            if type(data["date"]) != datetime.datetime:
                try:
                    data["date"] = datetime.datetime.strptime(data["date"], "%Y-%m-%d")
                except:
                    data["date"] = None

        super(PlaySession, self).__init__(data)

    def _format(self, log):
        log.info("play id         : {}".format(self.id))
        log.info("play user id    : {}".format(self.user_id))
        if self.date:
            log.info("play date       : {}".format(self.date.strftime("%Y-%m-%d")))
        log.info("play quantity   : {}".format(self.quantity))
        log.info("play duration   : {}".format(self.duration))
        log.info("play incomplete : {}".format(self.incomplete))
        log.info("play nowinstats : {}".format(self.nowinstats))
        log.info("play game       : {} ({})".format(self.game_name, self.game_id))
        log.info("play comment    : {}".format(self.comment))

    @property
    def id(self):
        """
        :return: the play session id
        """
        return self._data.get("id")

    @property
    def user_id(self):
        """
        :return: user ID whom this play session belongs to
        """
        return self._data.get("user_id")

    @property
    def date(self):
        """
        :return: the date when this play session was recorded
        """
        return self._data.get("date")

    @property
    def quantity(self):
        """
        :return:
        """
        return self._data.get("quantity")

    @property
    def duration(self):
        """
        :return: duration of the play session
        """
        return self._data.get("duration")

    @property
    def incomplete(self):
        """
        :return: whether the session was incomplete or not
        """
        return self._data.get("incomplete")

    @property
    def nowinstats(self):
        """
        :return:
        """
        return self._data.get("nowinstats")

    @property
    def game_id(self):
        """

        :return: id of the game played
        """
        return self._data.get("game_id")

    @property
    def game_name(self):
        """
        :return: name of the game played
        """
        return self._data.get("game_name")

    @property
    def comment(self):
        """
        :return: comment on the play session
        """
        return self._data.get("comment")


class Plays(DictObject):
    """
    A list of play sessions, associated either to an user or to a game.
    """

    def __init__(self, data):
        kw = copy(data)
        if "plays" not in kw:
            kw["plays"] = []
        self._plays = []

        for p in kw["plays"]:
            self._plays.append(PlaySession(p))

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

    def __getitem__(self, item):
        return self._plays.__getitem__(item)

    def __len__(self):
        return len(self._plays)

    def add_play(self, data):
        self._data["plays"].append(data)
        self._plays.append(PlaySession(data))

    @property
    def user(self):
        """
        :return: account name of the user owning this list of plays
        :return: ``None`` if this list is that of a game and not an user's
        """
        return self._data.get("username")

    @property
    def user_id(self):
        """

        :return: id of the user owning this list of plays
        :return: ``None`` if this list is that of a game and not an user's
        """
        return self._data.get("user_id")

    @property
    def game_id(self):
        """

        :return: id of the game this plays list belongs to
        :return: ``None`` if this list is that of an user
        """
        return self._data.get("game_id")

    @property
    def plays(self):
        """
        :return: list of :class:`PlaySession`
        """
        return self._plays