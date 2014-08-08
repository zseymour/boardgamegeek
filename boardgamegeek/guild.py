from .utils import DictObject


class Guild(DictObject):

    @property
    def category(self):
        return self._data.get("category")

    @property
    def name(self):
        return self._data.get("name")

    @property
    def id(self):
        return self._data.get("id")

    @property
    def members(self):
        return self._data.get("members")

    @property
    def description(self):
        return self._data.get("description")

    @property
    def manager(self):
        return self._data.get("manager")

    @property
    def website(self):
        return self._data.get("website")

    def __unicode__(self):
        return u"BGG guild: {}".format(self.name, self.id)

    def __repr__(self):
        return u"guild: {} (id: {})".format(self.name, self.id).encode("utf-8")