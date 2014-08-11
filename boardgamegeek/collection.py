from copy import copy
from collections import Iterable

from .games import CollectionBoardGame
from .utils import DictObject


class Collection(DictObject):

    def __init__(self, data):
        kw = copy(data)
        if "items" not in kw:
            kw["items"] = []
        super(Collection, self).__init__(kw)

    def _format(self, log):
        log.info(u"owner    : {}".format(self.owner))
        log.info(u"size     : {} items".format(len(self)))

        log.info(u"items")

        for i in self.iteritems():
            i._format(log)
            log.info("---------------------")

    def add_game(self, game):
        self._data["items"].append(game)

    def __unicode__(self):
        return "{}'s collection, {} items".format(self.username, len(self.games))

    def __len__(self):
        return len(self._data["items"])

    @property
    def owner(self):
        return self._data.get("owner")

    @property
    def size(self):
        return len(self._data["items"])

    @property
    def items(self):
        return [CollectionGame(x) for x in self._data["items"]]

    def iteritems(self):
        for item in self._data["items"]:
            yield CollectionGame(item)
