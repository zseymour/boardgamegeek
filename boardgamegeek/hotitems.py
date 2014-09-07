# coding: utf-8

"""
:mod:`boardgamegeek.hotitems` - BoardGameGeek "Hot Items"
=========================================================

.. module:: boardgamegeek.hotitems
   :platform: Unix, Windows
   :synopsis: BGG "Hot Items"

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""
from __future__ import unicode_literals

from copy import copy


from .things import Thing
from .utils import DictObject


class HotItem(Thing):
    """
    A hot item from a list. Can refer to either an item (``boardgame``, ``videogame``, etc.), a person (``rpgperson``, ``boardgameperson``)
    or even a company (``boardgamecompany``, ``videogamecompany``), depending on the type of hot list retrieved.
    """

    def __repr__(self):
        return "HotItem (id: {})".format(self.id)

    def _format(self, log):
        log.info("hot item id        : {}".format(self.id))
        log.info("hot item name      : {}".format(self.name))
        log.info("hot item rank      : {}".format(self.rank))
        log.info("hot item published : {}".format(self.year))
        log.info("hot item thumbnail : {}".format(self.thumbnail))

    @property
    def rank(self):
        """
        :return: Ranking of this hot item
        """
        return self._data["rank"]

    @property
    def year(self):
        """
        Year this item was published

        :return: integer representing the year
        :return: ``None`` if object doesn't refer to a game
        """
        return self._data.get("yearpublished")

    @property
    def thumbnail(self):
        """
        :return: url of the thumbnail corresponding to this item
        """
        return self._data.get("thumbnail")


class HotItems(DictObject):
    """
    A container for :class:`boardgamegeek.hotitems.HotItem`
    """
    def __init__(self, data):
        kw = copy(data)
        if "items" not in kw:
            kw["items"] = []

        self._items = []
        for data in kw["items"]:
            self._items.append(HotItem(data))

        super(HotItems, self).__init__(kw)

    def add_hot_item(self, data):
        """
        Add a new hot item to the container

        :param data: dictionary containing the data

        """
        self._data["items"].append(data)
        self._items.append(HotItem(data))

    @property
    def items(self):
        """

        :return: the list of :class:`boardgamegeek.hotitems.HotItem`
        """
        return self._items

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for item in self._data["items"]:
            yield HotItem(item)