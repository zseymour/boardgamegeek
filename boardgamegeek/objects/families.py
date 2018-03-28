# coding: utf-8
"""
:mod:`boardgamegeek.games` - Games information
==============================================

.. module:: boardgamegeek.objects.families
   :platform: Unix, Windows
   :synopsis: classes for storing family information

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>

"""
from __future__ import unicode_literals

import datetime
from copy import copy

from .things import Thing
from .games import BaseGame, BoardGameVideo, BoardGameComment
from ..exceptions import BGGError
from ..utils import fix_url, DictObject, fix_unsigned_negative


class Family(BaseGame):
    """
    Object containing information about a game family
    """
    def __init__(self, data):
        FAMILIY_TYPES = {"boardgamefamily":"BoardGameFamily",
                         "rpg":"RPG",
                         "rpgperiodical":"RPGPeriodical"}
        
        self.type = FAMILIY_TYPES[data["type"]]
        self._videos = []
        self._videos_ids = set()
        for video in data.get("videos", []):
            try:
                if video["id"] not in self._videos_ids:
                    self._videos.append(BoardGameVideo(video))
                    self._videos_ids.add(video["id"])
            except KeyError:
                raise BGGError("invalid video data")

        self._comments = []
        for comment in data.get("comments", []):
            self.add_comment(comment)

        super(Family, self).__init__(data)

    def __repr__(self):
        return "Family (id: {})".format(self.id)

    def add_comment(self, data):
        self._comments.append(BoardGameComment(data))

    def _format(self, log):
        log.info("rpg id      : {}".format(self.id))
        log.info("rpg name    : {}".format(self.name))
        log.info("rpg rank    : {}".format(self.bgg_rank))
        if self.alternative_names:
            for i in self.alternative_names:
                log.info("alternative name  : {}".format(i))
        log.info("thumbnail         : {}".format(self.thumbnail))
        log.info("image             : {}".format(self.image))

        if self.family_members:
            log.info("family members")
            for i in self.family_members[:10]:
                log.info("- {}".format(i))
            if len(self.family_members) > 10:
                log.info("- and {} more.".format(len(self.family_members) - 10))
                
        if self.videos:
            log.info("videos")
            for v in self.videos:
                v._format(log)
                log.info("--------")

        if self.versions:
            log.info("versions")
            for v in self.versions:
                v._format(log)
                log.info("--------")

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
        if self.comments:
            for c in self.comments:
                c._format(log)

    @property
    def alternative_names(self):
        """
        :return: alternative names
        :rtype: list of str
        """
        return self._data.get("alternative_names", [])

    @property
    def description(self):
        """
        :return: description
        :rtype: str
        """
        return self._data.get("description", "")

    @property
    def family_members(self):
        """
        :return: family_members
        :rtype: list of str
        """
        return self._data.get("family_members", [])

    @property
    def comments(self):
        return self._comments

    @property
    def mechanics(self):
        """
        :return: mechanics
        :rtype: list of str
        """
        return self._data.get("mechanics", [])

    @property
    def users_owned(self):
        """
        :return: number of users owning this game
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._stats.users_owned

    @property
    def users_trading(self):
        """
        :return: number of users trading this game
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._stats.users_trading

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
        return self._stats.rating_num_weights

    @property
    def rating_average_weight(self):
        """
        :return: average weight
        :rtype: float
        :return: ``None`` if n/a
        """
        return self._stats.rating_average_weight

    @property
    def videos(self):
        """
        :return: videos of this game
        :rtype: list of :py:class:`boardgamegeek.game.BoardGameVideo`
        """
        return self._videos

    @property
    def versions(self):
        """
        :return: versions of this game
        :rtype: list of :py:class:`boardgamegeek.game.BoardGameVersion`
        """
        return self._versions
        