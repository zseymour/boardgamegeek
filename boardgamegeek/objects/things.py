# coding: utf-8
"""
:mod:`boardgamegeek.things` - Generic objects
=============================================

.. module:: boardgamegeek.things
   :platform: Unix, Windows
   :synopsis: Generic objects

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>

"""
from __future__ import unicode_literals

from ..exceptions import BGGError
from ..utils import DictObject


class Thing(DictObject):
    """
    A thing, an object with a name and an id. Base class for various objects in the library.
    """
    def __init__(self, data):
        for i in ["id", "name"]:
            if i not in data:
                raise BGGError("missing '{}' when trying to create a Thing".format(i))

        try:
            self._id = int(data["id"])
        except:
            raise BGGError("id ({}) is not an int when trying to create a Thing".format(data["id"]))

        self._name = data["name"]

        super(Thing, self).__init__(data)

    @property
    def name(self):
        """
        :return: name
        :rtype: str
        """
        return self._name

    @property
    def id(self):
        """
        :return: id
        :rtype: integer
        """
        return self._id

    def __repr__(self):
        return "{} (id: {})".format(self.__name__, self.id)
