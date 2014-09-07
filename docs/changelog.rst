Changelog
=========

0.3.0
-----

Changes

  * Added a property to :class:`boardgamegeek.games.BoardGame`, ``expansion`` which indicates if this item is an expansion or not
  * Changed the ``expansions`` property of :class:`boardgamegeek.games.BoardGame`, now it returns a list of :class:`boardgamegeek.things.Thing` for each expansion the game has
  * Added a property to :class:`boardgamegeek.games.BoardGame`, ``extends`` which returns a list of :class:`boardgamegeek.things.Thing` for each item this game is an extension to


0.2.0 (unreleased)
------------------

Changes

  * Changed the object hierarchy, replaced ``BasicUser``, ``BasicGuild``, ``BasicGame`` with a :class:`boardgamegeek.things.Thing`
    which has a name and an id

Features

  * Added support for retrieving the hot lists


0.1.0
-----

Features

  * Allowing the user to specify timeouts for the requests library

0.0.14
------

Changes

  * The ``.last_login`` property of an :class:`boardgamegeek.user.User` object now returns a ``datetime.datetime``

Features

  * Added support for an user's top and hot lists

Bugfixes

  * Exceptions raised from :func:`get_parsed_xml_response` where not properly propagated to the calling code

0.0.13
------

Features

  * Improved code for fetching an user's buddies and guilds
  * Improved code for fetching guild members
  * Added support for listing Plays by user and by game


0.0.12
------

Features

  * Added some basic argument validation to prevent pointless calls to BGG's API
  * When some object (game, user name, etc.) is not found, the functions return None instead of raising an exception


0.0.11
------

Features

  * Collections and Guilds are now iterable

Bugfixes

  * Fixed __str__ for Collection

0.0.10
------

Features

  * Updated documentation
  * Improved Python 3.x compatibility (using unicode_literals)
  * Added Travis integration

Bugfixes

  * Fixed float division for Python 3.x

0.0.9
-----

Features

  * Added support for retrieving an user's buddy and guild lists
  * Started implementing some basic unit tests

Bugfixes

  * Fixed handling of non-existing user names
  * Properly returning the maximum number of players for a game