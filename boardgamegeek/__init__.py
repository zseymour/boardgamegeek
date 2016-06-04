# coding: utf-8
"""
.. module:: boardgamegeek
   :platform: Unix, Windows
   :synopsis: interface to boardgamegeek.com

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""
from .api import BoardGameGeek
from .exceptions import BGGError, BGGApiRetryError, BoardGameGeekAPIError, BGGApiTimeoutError
from .version import __version__

__all__ = [BoardGameGeek, BGGApiRetryError, BGGError, BoardGameGeekAPIError, BGGApiTimeoutError]
__import__('pkg_resources').declare_namespace(__name__)