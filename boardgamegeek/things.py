from __future__ import unicode_literals

from .utils import DictObject


class Thing(DictObject):
    """
    A thing, in BGG's API conception, having a name and an id
    """
    @property
    def name(self):
        return self._data.get("name")

    @property
    def id(self):
        return self._data.get("id")

    def __repr__(self):
        return "Thing (id: {})".format(self.id)