# coding: utf-8
"""
:mod:`boardgamegeek.exceptions` - Exceptions
============================================

.. module:: boardgamegeek.exceptions
   :platform: Unix, Windows
   :synopsis: exceptions used in the package

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""


class BoardGameGeekError(Exception):
    pass


class BoardGameGeekTimeoutError(BoardGameGeekError):
    pass


class BoardGameGeekAPIError(BoardGameGeekError):
    """ An error related to the BGG XML2 API """
    pass


class BoardGameGeekAPIRetryError(BoardGameGeekAPIError):
    """ The request to the BGG XML2 API should be retried """
    pass


class BoardGameGeekAPINonXMLError(BoardGameGeekAPIError):
    """ The BGG XML2 API returned a non-XML response """
    pass
