==================================================
boardgamegeek - A Python API for boardgamegeek.com
==================================================


.. image:: https://travis-ci.org/lcosmin/boardgamegeek.svg?branch=master
    :target: https://travis-ci.org/lcosmin/boardgamegeek


.. image:: https://coveralls.io/repos/lcosmin/boardgamegeek/badge.png?branch=master
  :target: https://coveralls.io/r/lcosmin/boardgamegeek?branch=master


Introduction
============


``boardgamegeek`` is a Python library which makes it easy to access data from BoardGameGeek_ using their official XML
API.

It's an almost completely rewritten fork of libBGG_.


.. warning::
    The module's API is still considered unstable at this point and it might change in the future, especially if wanting
    to add support for the other sites.

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

If you want to use the disk cache:

.. code-block:: pycon

    >>> bgg = BoardGameGeek(cache="sqlite:///tmp/cache.db?ttl=3600&fast_save=0")
    >>> g = bgg.game("Celtica")
    >>> g.id
    21293

To Do
=====

* Not all the information exposed by the official API is stored into the Python objects. Need to improve this.
* Try to support the other sites from the boardgamegeek's family
* Improve documentation :)
* Improve unit testing

Contributions/suggestions are welcome.


.. _BoardGameGeek: http://www.boardgamegeek.com
.. _libBGG: https://github.com/philsstein/libBGG
.. _requests-cache: https://pypi.python.org/pypi/requests-cache
