from .utils import DictObject


class User(DictObject):

    # FIXME: look for an user with top10 and hot10

    def __unicode__(self):
        return u"user: {} {}".format(self.firstname, self.lastname)

    def __repr__(self):
        return u"username: {} (id: {})".format(self.name, self.id).encode("utf-8")

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