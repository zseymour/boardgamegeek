from __future__ import unicode_literals

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
        log.info("id         : {}".format(self.id))
        log.info("name       : {}".format(self.name))
        log.info("category   : {}".format(self.category))
        log.info("manager    : {}".format(self.manager))
        log.info("website    : {}".format(self.website))
        log.info("description: {}".format(self.description))
        log.info("country    : {}".format(self.country))
        log.info("state      : {}".format(self.state))
        log.info("city       : {}".format(self.city))
        log.info("address    : {}".format(self.address))
        log.info("postal code: {}".format(self.postalcode))
        if self.members:
            log.info("{} members".format(len(self.members)))
            for i in self.members:
                log.info(" - {}".format(i))

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
        return "BGG guild: {}".format(self.name, self.id)

    def __repr__(self):
        return "guild: {} (id: {})".format(self.name, self.id).encode("utf-8")