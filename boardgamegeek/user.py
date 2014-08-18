from copy import copy

from .guild import BasicGuild
from .utils import DictObject


class BasicUser(DictObject):
    """
    A basic user which holds information common to all user types
    """
    @property
    def name(self):
        return self._data.get("name")

    @property
    def id(self):
        return self._data.get("id")


class User(BasicUser):
    """
    Regular user
    """
    def __init__(self, data):
        kw = copy(data)
        if "buddies" not in kw:
            kw["buddies"] = []
        if "guilds" not in kw:
            kw["guilds"] = []
        super(User, self).__init__(kw)

    def __unicode__(self):
        return u"user: {} {}".format(self.firstname, self.lastname)

    def __repr__(self):
        return u"username: {} (id: {})".format(self.name, self.id).encode("utf-8")

    def add_buddy(self, data):
        self._data["buddies"].append(data)

    def add_guild(self, data):
        self._data["guilds"].append(data)

    def _format(self, log):
        log.info(u"id          : {}".format(self.id))
        log.info(u"login name  : {}".format(self.name))
        log.info(u"first name  : {}".format(self.firstname))
        log.info(u"last name   : {}".format(self.lastname))
        log.info(u"state       : {}".format(self.state))
        log.info(u"country     : {}".format(self.country))
        log.info(u"home page   : {}".format(self.homepage))
        log.info(u"avatar      : {}".format(self.avatar))
        log.info(u"xbox acct   : {}".format(self.xbox_account))
        log.info(u"wii acct    : {}".format(self.wii_account))
        log.info(u"steam acct  : {}".format(self.steam_account))
        log.info(u"psn acct    : {}".format(self.psn_account))
        log.info(u"last login  : {}".format(self.last_login))
        log.info(u"trade rating: {}".format(self.trade_rating))

        log.info(u"user has {} buddies{}".format(self.total_buddies,
                                                 " (forever alone :'( )" if self.total_buddies == 0 else ""))
        buddies = self.buddies
        if buddies:
            for b in buddies:
                log.info(u"- {}".format(b.name))

        log.info(u"user is member in {} guilds".format(self.total_guilds))
        guilds = self.guilds
        if guilds:
            for g in guilds:
                log.info(u"- {}".format(g.name))

    @property
    def total_buddies(self):
        return len(self._data["buddies"])

    @property
    def total_guilds(self):
        return len(self._data["guilds"])

    @property
    def buddies(self):
        return [BasicUser(x) for x in self._data["buddies"]]

    @property
    def guilds(self):
        return [BasicGuild(x) for x in self._data["guilds"]]

    @property
    def firstname(self):
        return self._data.get("firstname")

    @property
    def lastname(self):
        return self._data.get("lastname")

    @property
    def avatar(self):
        return self._data.get("avatarlink")

    @property
    def last_login(self):
        return self._data.get("lastlogin")

    @property
    def state(self):
        return self._data.get("stateorprovince")

    @property
    def country(self):
        return self._data.get("country")

    @property
    def homepage(self):
        return self._data.get("webaddress")

    @property
    def xbox_account(self):
        return self._data.get("xboxaccount")

    @property
    def wii_account(self):
        return self._data.get("wiiaccount")

    @property
    def steam_account(self):
        return self._data.get("steam_account")

    @property
    def psn_account(self):
        return self._data.get("psnaccount")

    @property
    def trade_rating(self):
        return self._data.get("trade_rating")