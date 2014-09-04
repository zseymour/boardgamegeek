# coding: utf-8
"""
:mod:`boardgamegeek.user` - Generic objects
===========================================

.. module:: boardgamegeek.user
   :platform: Unix, Windows
   :synopsis: Generic objects

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>

"""
from __future__ import unicode_literals

from .utils import DictObject


class Thing(DictObject):
    """
    A thing, an object with a name and an id
    """
    @property
    def name(self):
        return self._data.get("name")

    @property
    def id(self):
        return self._data.get("id")

    def __repr__(self):
        return "Thing (id: {})".format(self.id)