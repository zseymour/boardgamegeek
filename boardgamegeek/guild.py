from .utils import DictObject


class Guild(DictObject):

    def _format(self, log):
        log.info(u"id         : {}".format(self.id))
        log.info(u"name       : {}".format(self.name))
        log.info(u"category   : {}".format(self.category))
        log.info(u"manager    : {}".format(self.manager))
        log.info(u"website    : {}".format(self.website))
        log.info(u"description: {}".format(self.description))
        if self.members:
            log.info(u"members")
            for i in self.members:
                log.info(u" - {}".format(i))

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