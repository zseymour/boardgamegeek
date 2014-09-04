from __future__ import unicode_literals

from copy import copy


from .things import Thing
from .utils import DictObject


class HotItem(Thing):
    """
    An item from a "hotness" list on BGG
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
        return self._data["rank"]

    @property
    def year(self):
        return self._data.get("yearpublished")

    @property
    def thumbnail(self):
        return self._data.get("thumbnail")


class HotItems(DictObject):

    def __init__(self, data):
        kw = copy(data)
        if "items" not in kw:
            kw["items"] = []
        self._items = []
        super(HotItems, self).__init__(kw)

    def add_hot_item(self, data):
        self._data["items"].append(data)
        self._items.append(HotItem(data))

    @property
    def items(self):
        return self._items

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for item in self._data["items"]:
            yield HotItem(item)