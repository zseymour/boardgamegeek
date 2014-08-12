==================================================
boardgamegeek - A Python API for boardgamegeek.com
==================================================


Introduction
============


``boardgamegeek`` is a Python library which makes it easy to access data off BoardGameGeek_ using their official XML
API.

It's an almost completely rewritten fork of libBGG_.


.. warning::
    The module's API is still considered unstable at this point and it might change in the future, especially if wanting
    to add support for the other sites.

Features
========

This library exposes (as Python objects with properties) the following BoardGameGeek_ entities:

* Users
* Games
* User collections
* Player guilds

requests-cache_ is used for locally caching replies in order to reduce the amount of requests sent to the server.

.. warning::
    At the moment, the cache is enabled by default and it's configured to save data in an Sqlite database
    in the current directory.

Quick Install
=============

To install ``boardgamegeek``, just use pip::

    > pip install boardgamegeek


Documentation
=============

Documentation is available at http://boardgamegeek.readthedocs.org/


Usage
=====

Here's a quick usage example:

.. code-block:: pycon

    >>> from boardgamegeek import BoardGameGeek
    >>> bgg = BoardGameGeek()
    >>> g = bgg.game("Android: Netrunner")
    >>> g.name
    'Android: Netrunner'
    >>> g.id
    124742
    >>> for n in g.alternative_names: print n.encode("utf-8")
    ...
    安卓纪元：矩阵潜袭


To Do
=====

* Not all the information exposed by the official API is stored into the Python objects. Need to improve this.
* Try to support the other sites from the boardgamegeek's family
* Allow better control for configuring the cache
* Improve documentation :)


Contributions/suggestions are welcome.


.. _BoardGameGeek: http://www.boardgamegeek.com
.. _libBGG: https://github.com/philsstein/libBGG
.. _requests-cache: https://pypi.python.org/pypi/requests-cache