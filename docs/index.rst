.. boardgamegeek documentation master file, created by
   sphinx-quickstart on Tue Aug 12 13:41:37 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

boardgamegeek - A Python API for boardgamegeek.com
==================================================


Introduction
============


``boardgamegeek`` is a Python library which makes it easy to access data off BoardGameGeek_ using their official XML
API. It's an almost completely rewritten fork of libBGG_.

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



Usage
=====

Here's a quick usage example::

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
* Improve documentation :)


Contributions/suggestions are welcome.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _BoardGameGeek: http://www.boardgamegeek.com
.. _libBGG: https://github.com/philsstein/libBGG