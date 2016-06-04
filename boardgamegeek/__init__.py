# coding: utf-8
"""
.. module:: boardgamegeek
   :platform: Unix, Windows
   :synopsis: interface to boardgamegeek.com

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""
from .api import BoardGameGeek
from .exceptions import BGGError, BGGApiRetryError, BGGApiError, BGGApiTimeoutError
from .cache import CacheBackendNone, CacheBackendMemory, CacheBackendSqlite
from .version import __version__

__all__ = [BoardGameGeek, BGGError, BGGApiRetryError, BGGApiError, BGGApiTimeoutError]
__import__('pkg_resources').declare_namespace(__name__)


