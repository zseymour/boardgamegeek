Changelog
=========

0.8.1
-----

Fixes

  * Infinite recursion when unpickling objects

0.8.0
-----

Features

  * Fetching plays has support for min_date, max_date (thanks tomusher!) 

0.7.1
-----

Fixes
  
  * Not expecting the score of a player to be a number anymore (using the string as returned by the BGG API)

0.7.0
-----

Changes

  * The XML API2 seems to throttle requests by returning HTTP 503 ; added a delay and retry in the code to try
    to deal with this

Features

  * When retrieving the plays, players are also returned, along with their data.


0.6.0
-----

Changes

  * Improved code in an attempt to prevent exceptions when trying to deal with invalid data coming from the remote XML data
 
Fixes
  
  * Fixed issue #12 (an edge case which lead to comparing None to int)

0.5.0
-----
  
Features

  * Added a new function :py:func:`boardgamegeek.api.BoardGameGeek.games()` which takes a name as argument and returns a list of :py:class:`boardgamegeek.games.BoardGame` with 
    all the games with that name.

0.4.3
-----

Changes

  * When calling :py:func:`boardgamegeek.api.BoardGameGeek.game()` with a name, return the most recently published result instead of the first one, in case of multiple results.

0.4.2
-----

Changes

  * Increased default number of retries and timeout 

0.4.0
-----

Changes

  * The calls to the BGG API will be automatically retried two times, with a timeout of 10 seconds. This behaviour can
    be controlled via the retries=, timeout= and retry_delay= parameters.

Features

  * Added patch from philsstein to automatically increase timeout and retry request on timeout

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
