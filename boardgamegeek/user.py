from .utils import DictObject


class User(DictObject):

    # FIXME: look for an user with top10 and hot10

    def __unicode__(self):
        return u"user: {} {}".format(self.firstname, self.lastname)

    def __repr__(self):
        return u"username: {} (id: {})".format(self.name, self.id).encode("utf-8")

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

    @property
    def name(self):
        return self._data.get("name")

    @property
    def id(self):
        return self._data.get("id")

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