from .utils import DictObject


class BasicGuild(DictObject):
    """
    Basic guild information, name and id.
    """
    @property
    def name(self):
        return self._data.get("name")

    @property
    def id(self):
        return self._data.get("id")


class Guild(BasicGuild):

    def _format(self, log):
        log.info(u"id         : {}".format(self.id))
        log.info(u"name       : {}".format(self.name))
        log.info(u"category   : {}".format(self.category))
        log.info(u"manager    : {}".format(self.manager))
        log.info(u"website    : {}".format(self.website))
        log.info(u"description: {}".format(self.description))
        log.info(u"country    : {}".format(self.country))
        log.info(u"state      : {}".format(self.state))
        log.info(u"city       : {}".format(self.city))
        log.info(u"address    : {}".format(self.address))
        log.info(u"postal code: {}".format(self.postalcode))
        if self.members:
            log.info(u"{} members".format(len(self.members)))
            for i in self.members:
                log.info(u" - {}".format(i))

    @property
    def country(self):
        return self._data.get("country")

    @property
    def city(self):
        return self._data.get("city")

    @property
    def address(self):
        """
        :return: Both address fields concatenated
        """
        address = ""
        if self._data.get("addr1"):
            address += self._data.get("addr1")

        if self._data.get("addr2"):
            if len(address):
                address += " "  # delimit the two address fields by a space
            address += self._data.get("addr2")

        return address if len(address) else None

    @property
    def addr1(self):
        return self._data.get("addr1")

    @property
    def addr2(self):
        return self._data.get("addr2")

    @property
    def postalcode(self):
        return self._data.get("postalcode")

    @property
    def state(self):
        return self._data.get("stateorprovince")

    @property
    def category(self):
        return self._data.get("category")

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