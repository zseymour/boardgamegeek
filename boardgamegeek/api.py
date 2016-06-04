# coding: utf-8
"""
:mod:`boardgamegeek.api` - Core functions
=========================================

This module contains the core functionality needed to retrieve data from boardgamegeek.com and parse it into usable
objects.

.. module:: boardgamegeek.api
   :platform: Unix, Windows
   :synopsis: module handling communication with the online BoardGameGeek API

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""
from __future__ import unicode_literals

import datetime
import logging
import sys
import warnings

# This is required for decoding HTML entities from the description text
# of games
if sys.version_info >= (3,):
    import html.parser as hp
else:
    import HTMLParser as hp


from .objects.user import User
from .objects.search import SearchResult

from .exceptions import BGGApiError, BGGError, BGGItemNotFoundError
from .utils import xml_subelement_attr, request_and_parse_xml
from .utils import RateLimitingAdapter, DEFAULT_REQUESTS_PER_MINUTE
from .cache import CacheBackendMemory

from .loaders import create_guild_from_xml, add_guild_members_from_xml
from .loaders import create_plays_from_xml, add_plays_from_xml
from .loaders import create_hot_items_from_xml, add_hot_items_from_xml
from .loaders import create_collection_from_xml, add_collection_items_from_xml
from .loaders import create_game_from_xml, add_game_comments_from_xml


log = logging.getLogger("boardgamegeek.api")
html_parser = hp.HTMLParser()

HOT_ITEM_CHOICES = ["boardgame", "rpg", "videogame", "boardgameperson", "rpgperson", "boardgamecompany",
                    "rpgcompany", "videogamecompany"]

COLLECTION_SUBTYPES = ["boardgame", "boardgameexpansion", "boardgameaccessory", "rpgitem", "rpgissue", "videogame"]


def call_progress_cb(progress_cb, current, total):
    if progress_cb is not None:
        progress_cb(current, total)


class BoardGameGeekNetworkAPI(object):
    """
    Base class for the BoardGameGeek websites APIs. All site-specific clients are derived from this.

    :param str api_endpoint: URL of the API
    :param str cache: instance of a :py:class:`boardgamegeek.cache.CacheBackend` class
    :param integer timeout: timeout for a request
    :param integer retries: how many retries to perform in special cases
    :param integer retry_delay: delay between retries (seconds)
    """
    SEARCH_RPG_ITEM = 1
    SEARCH_VIDEO_GAME = 2
    SEARCH_BOARD_GAME = 4
    SEARCH_BOARD_GAME_EXPANSION = 8

    def __init__(self, api_endpoint, cache, timeout, retries, retry_delay, requests_per_minute):
        self._search_api_url = api_endpoint + "/search"
        self._thing_api_url = api_endpoint + "/thing"
        self._guild_api_url = api_endpoint + "/guild"
        self._user_api_url = api_endpoint + "/user"
        self._plays_api_url = api_endpoint + "/plays"
        self._hot_api_url = api_endpoint + "/hot"
        self._collection_api_url = api_endpoint + "/collection"
        self._timeout = timeout
        self._retries = retries
        self._retry_delay = retry_delay
        self.requests_session = cache.cache

        # add the rate limiting adapter
        self.requests_session.mount(api_endpoint, RateLimitingAdapter(rpm=requests_per_minute))

    def _get_game_id(self, name, game_type, choose):
        """
        Returns the BGG ID of a game, searching by name

        :param str name: the name of the game to search for
        :param str game_type: the game type ("rpgitem", "videogame", "boardgame", "boardgameexpansion")
        :param str choose: method of selecting the game by name, when dealing with multiple results. Valid values are "first", "recent" or "best-rank"
        :return: ``None`` if game wasn't found
        :return: game's id
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekError` in case of invalid name
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIRetryError` if this request should be retried after a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekTimeoutError` if there was a timeout
        """

        if choose not in ["first", "recent", "best-rank"]:
            raise BGGError("invalid value for parameter 'choose': {}".format(choose))

        log.debug("getting game id for '{}'".format(name))
        res = self.search(name, search_type=[game_type], exact=True)

        if not res:
            raise BGGItemNotFoundError("can't find '{}'".format(name))

        if choose == "first":
            return res[0].id
        elif choose == "recent":
            # choose the result with the biggest year
            return max(res, key=lambda x: x.year if x.year is not None else -300000).id
        else:
            # getting the best rank requires fetching the data of all games returned
            game_data = [self.game(game_id=r.id) for r in res]
            # ...and selecting the one with the best ranking
            return min(game_data, key=lambda x: x.boardgame_rank if x.boardgame_rank is not None else 10000000000).id

    def guild(self, guild_id, progress=None):
        """
        Retrieves details about a guild

        :param integer guild_id: the id number of the guild
        :param callable progress: an optional callable for reporting progress, taking two integers (``current``, ``total``) as arguments
        :return: ``Guild`` object containing the data
        :return: ``None`` if the information couldn't be retrieved
        :rtype: :py:class:`boardgamegeek.guild.Guild`
        :raises: :py:exc:`BGGError` in case of an invalid guild id
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiRetryError` if this request should be retried after a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiTimeoutError` if there was a timeout
        """

        try:
            guild_id = int(guild_id)
        except:
            raise BGGError("invalid guild id")

        xml_root = request_and_parse_xml(self.requests_session,
                                         self._guild_api_url,
                                         params={"id": guild_id, "members": 1},
                                         timeout=self._timeout,
                                         retries=self._retries,
                                         retry_delay=self._retry_delay)


        try:
            guild = create_guild_from_xml(xml_root, html_parser)
        except BGGError as e:
            log.error("error getting guild data: {}".format(e))
            # TODO: raise exception
            return None

        # Add the first page of members
        try:
            added_member = add_guild_members_from_xml(guild, xml_root)
            call_progress_cb(progress, len(guild), guild.members_count)
        except BGGError as e:
            log.error("error adding guild members: {}".format(e))
            # TODO: add flag about fetching guild members error
            return guild

        # Fetch the other pages of members
        page = 1
        while len(guild) < guild.members_count and added_member:
            page += 1
            log.debug("fetching page {}".format(page))
            try:
                xml_root = request_and_parse_xml(self.requests_session,
                                                 self._guild_api_url,
                                                 params={"id": guild_id, "members": 1, "page": page},
                                                 timeout=self._timeout,
                                                 retries=self._retries,
                                                 retry_delay=self._retry_delay)
            except BGGApiError:
                log.debug("non-XML response while loading guild members")
                # TODO: flag error
                break

            try:
                added_member = add_guild_members_from_xml(guild, xml_root)
                call_progress_cb(progress, len(guild), guild.members_count)
            except BGGError as e:
                log.error("error adding guild members: {}".format(e))
                break
                # TODO: decide if in this case we should return the guild object or None in case of error

        return guild

    # TODO: refactor
    def user(self, name, progress=None, buddies=True, guilds=True, hot=True, top=True, domain="boardgame"):
        """
        Retrieves details about an user

        :param str name: user's login name
        :param callable progress: an optional callable for reporting progress when fetching the buddy list/guilds,
                                  taking two integers (``current``, ``total``) as arguments
        :param bool buddies: if ``True``, get the user's buddies
        :param bool guilds: if ``True``, get the user's guilds
        :param bool hot: if ``True``, get the user's "hot" list
        :param bool top: if ``True``, get the user's "top" list
        :param str domain: restrict items on the "hot" and "top" lists to ``domain``. Valid values are "boardgame" (default), "rpg" and "videogame"
        :return: ``User`` object
        :rtype: :py:class:`boardgamegeek.user.User`
        :return: ``None`` if the user couldn't be found

        :raises: :py:exc:`boardgamegeek.exceptions.BGGError` in case of invalid user name
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiRetryError` if this request should be retried after a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiTimeoutError` if there was a timeout
        """

        if not name:
            raise BGGError("no user name specified")

        if domain not in ["boardgame", "rpg", "videogame"]:
            raise BGGError("invalid 'domain'")

        params = {"name": name,
                  "buddies": 1 if buddies else 0,
                  "guilds": 1 if guilds else 0,
                  "hot": 1 if hot else 0,
                  "top": 1 if top else 0,
                  "domain": domain}

        root = request_and_parse_xml(self.requests_session,
                                     self._user_api_url,
                                     params=params,
                                     timeout=self._timeout,
                                     retries=self._retries,
                                     retry_delay=self._retry_delay)

        # when the user is not found, the API returns an response, but with most fields empty. id is empty too
        try:
            data = {"name": root.attrib["name"],
                    "id": int(root.attrib["id"])}
        except (KeyError, ValueError):
            raise BGGItemNotFoundError

        for i in ["firstname", "lastname", "avatarlink",
                  "stateorprovince", "country", "webaddress", "xboxaccount",
                  "wiiaccount", "steamaccount", "psnaccount", "traderating"]:
            data[i] = xml_subelement_attr(root, i)

        data["yearregistered"] = xml_subelement_attr(root, "yearregistered", convert=int, quiet=True)
        data["lastlogin"] = xml_subelement_attr(root,
                                                "lastlogin",
                                                convert=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"),
                                                quiet=True)

        # TODO: get rid of the add_top/hot_item methods, move them in the
        user = User(data)

        # add top items
        for top_item in root.findall(".//top/item"):
            user.add_top_item({"id": int(top_item.attrib["id"]),
                               "name": top_item.attrib["name"]})

        # add hot items
        for hot_item in root.findall(".//hot/item"):
            user.add_hot_item({"id": int(hot_item.attrib["id"]),
                               "name": hot_item.attrib["name"]})

        total_buddies = 0
        total_guilds = 0

        buddies = root.find("buddies")
        if buddies is not None:
            total_buddies = int(buddies.attrib["total"])
            if total_buddies > 0:
                # add the buddies from the first page
                for buddy in buddies.findall(".//buddy"):
                    user.add_buddy({"name": buddy.attrib["name"],
                                    "id": buddy.attrib["id"]})

        guilds = root.find("guilds")
        if guilds is not None:
            total_guilds = int(guilds.attrib["total"])
            if total_guilds > 0:
                # add the guilds from the first page
                for guild in guilds.findall(".//guild"):
                    user.add_guild({"name": guild.attrib["name"],
                                    "id": guild.attrib["id"]})

        # It seems that the BGG API can return more results than what's specified in the documentation (they say
        # page size is 100, but for an user with 114 friends, all buddies are there on the first page).
        # Therefore, we'll keep fetching pages until we reach the number of items we're expecting or we don't get
        # any more data

        max_items_to_fetch = max(total_buddies, total_guilds)

        def _call_progress_cb():
            if progress is not None:
                progress(max(user.total_buddies, user.total_guilds), max_items_to_fetch)

        _call_progress_cb()

        page = 2
        while max(user.total_buddies, user.total_guilds) < max_items_to_fetch:
            added_buddy = False
            added_guild = False
            params["page"] = page
            root = request_and_parse_xml(self.requests_session,
                                         self._user_api_url,
                                         params=params,
                                         timeout=self._timeout)

            for buddy in root.findall(".//buddy"):
                user.add_buddy({"name": buddy.attrib["name"],
                                "id": buddy.attrib["id"]})
                added_buddy = True

            for guild in root.findall(".//guild"):
                user.add_guild({"name": guild.attrib["name"],
                                "id": guild.attrib["id"]})
                added_guild = True

            _call_progress_cb()
            page += 1

            if not added_buddy and not added_guild:
                log.debug("didn't add any buddy/guild after fetching page {}, stopping here".format(page))
                break

        return user

    def plays(self, name=None, game_id=None, progress=None, min_date=None, max_date=None, subtype="boardgame"):
        """
        Retrieves the plays for an user (if using ``name``) or for a game (if using ``game_id``)

        :param str name: user name to retrieve the plays for
        :param integer game_id: game id to retrieve the plays for
        :param callable progress: an optional callable for reporting progress, taking two integers (``current``,
                                  ``total``) as arguments
        :param datetime.date min_date: return only plays of the specified date or later
        :param datetime.date max_date: return only plays of the specified date or earlier
        :param str subtype: limit plays results to the specified subtype. Valid values: "boardgame", "boardgameexpansion",
                            "boardgameaccessory", "rpgitem", "videogame"
        :return: object containing all the plays
        :rtype: :py:class:`boardgamegeek.plays.Plays`
        :return: ``None`` if the user/game couldn't be found
        :raises: :py:exc:`boardgamegeek.exceptions.BGGError` on errors
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiRetryError` if this request should be retried after a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiTimeoutError` if there was a timeout

        """
        if not name and not game_id:
            raise BGGError("no user name specified")

        if name and game_id:
            raise BGGError("can't retrieve by user and by game at the same time")

        if subtype not in ["boardgame", "boardgameexpansion", "boardgameaccessory", "rpgitem", "videogame"]:
            raise BGGError("invalid 'subtype'")

        params = {"subtype": subtype}

        if name:
            params["username"] = name
            game_id = None
        else:
            try:
                params["id"] = int(game_id)
            except BGGError:
                raise BGGError("invalid game id")

        if min_date:
            try:
                params["mindate"] = min_date.isoformat()
            except AttributeError:
                raise BGGError("mindate must be a datetime.date object")

        if max_date:
            try:
                params["maxdate"] = max_date.isoformat()
            except AttributeError:
                raise BGGError("maxdate must be a datetime.date object")

        xml_root = request_and_parse_xml(self.requests_session,
                                         self._plays_api_url,
                                         params=params,
                                         timeout=self._timeout,
                                         retries=self._retries,
                                         retry_delay=self._retry_delay)

        plays = create_plays_from_xml(xml_root, game_id)

        try:
            added_plays = add_plays_from_xml(plays, xml_root)
            call_progress_cb(progress, len(plays), plays.plays_count)
        except BGGError as e:
            log.error("error adding plays: {}".format(e))
            return plays

        page = 1

        # Since the BGG API doesn't seem to report the total number of plays for games correctly (it's 0), just
        # continue until we can't add anymore
        while added_plays:
            page += 1
            log.debug("fetching page {} of plays".format(page))

            params["page"] = page

            try:
                # fetch the next pages of plays
                xml_root = request_and_parse_xml(self.requests_session,
                                                 self._plays_api_url,
                                                 params=params,
                                                 timeout=self._timeout,
                                                 retries=self._retries,
                                                 retry_delay=self._retry_delay)
            except BGGError:
                break

            try:
                added_plays = add_plays_from_xml(plays, xml_root)
                call_progress_cb(progress, len(plays), plays.plays_count)
            except BGGError as e:
                log.error("error adding plays: {}".format(e))
                # TODO: error flag?
                break

        return plays

    def hot_items(self, item_type):
        """
        Return the list of "Hot Items"

        :param str item_type: hot item type. Valid values: "boardgame", "rpg", "videogame", "boardgameperson",
                              "rpgperson", "boardgamecompany", "rpgcompany", "videogamecompany")
        :return: ``HotItems`` object
        :rtype: :py:class:`boardgamegeek.hotitems.HotItems`
        :return: ``None`` in case the hot items couldn't be retrieved

        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekError` if the parameter is invalid
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIRetryError` if this request should be retried after
                  a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekTimeoutError` if there was a timeout
        """
        if item_type not in HOT_ITEM_CHOICES:
            raise BGGError("invalid type specified")

        params = {"type": item_type}

        xml_root = request_and_parse_xml(self.requests_session,
                                         self._hot_api_url,
                                         params=params,
                                         timeout=self._timeout,
                                         retries=self._retries,
                                         retry_delay=self._retry_delay)

        try:
            hot_items = create_hot_items_from_xml(xml_root)
        except BGGError as e:
            log.error("error getting hot items data: {}".format(e))
            # TODO raise error
            return None

        try:
            add_hot_items_from_xml(hot_items, xml_root)
        except BGGError as e:
            log.error("error adding hot items: {}".format(e))

        return hot_items

    def collection(self, user_name, subtype="boardgame", exclude_subtype=None, ids=None, versions=False,
                   own=None, rated=None, played=None, commented=None, trade=None, want=None, wishlist=None,
                   wishlist_prio=None, preordered=None, want_to_play=None, want_to_buy=None, prev_owned=None,
                   has_parts=None, want_parts=None, min_rating=None, rating=None, min_bgg_rating=None, bgg_rating=None,
                   min_plays=None, max_plays=None, collection_id=None, modified_since=None):
        """
        Returns an user's game collection

        :param str user_name: user name to retrieve the collection for
        :param str subtype: what type of items to return. One of: boardgame, boardgameexpansion, boardgameaccessory,
                            rpgitem, rpgissue, or videogame
        :param str exclude_subtype: if not ``None`` (default), exclude the specified subtype. One of: boardgame,
                                    boardgameexpansion, boardgameaccessory, rpgitem, rpgissue, or videogame
        :param list ids: if not ``None`` (default), limit the results to the specified ids.
        :param bool versions: include item version information
        :param bool own: include (if ``True``) or exclude (if ``False``) owned items
        :param bool rated: include (if ``True``) or exclude (if ``False``) rated items
        :param bool played: include (if ``True``) or exclude (if ``False``) played items
        :param bool commented: include (if ``True``) or exclude (if ``False``) items commented on
        :param bool trade: include (if ``True``) or exclude (if ``False``) items for trade
        :param bool want: include (if ``True``) or exclude (if ``False``) items wanted in trade
        :param bool wishlist: include (if ``True``) or exclude (if ``False``) items in the wishlist
        :param int wishlist_prio: return only the items with the specified wishlist priority (valid values: 1 to 5)
        :param bool preordered: include (if ``True``) or exclude (if ``False``) preordered items
        :param bool want_to_play: include (if ``True``) or exclude (if ``False``) items wanting to play
        :param bool want_to_buy: include (if ``True``) or exclude (if ``False``) items wanting to buy
        :param bool prev_owned: include (if ``True``) or exclude (if ``False``) previously owned items
        :param bool has_parts: include (if ``True``) or exclude (if ``False``) items for which there is a comment in the
                               "Has parts" field
        :param bool want_parts: include (if ``True``) or exclude (if ``False``) items for which there is a comment in
                                the "Want parts" field
        :param double min_rating: return items rated by the user with a minimum of ``min_rating``
        :param double rating: return items rated by the user with a maximum of ``rating``
        :param double min_bgg_rating : return items rated on BGG with a minimum of ``min_bgg_rating``
        :param double bgg_rating: return items rated on BGG with a maximum of ``bgg_rating``
        :param int collection_id: restrict results to the collection specified by this id
        :param str modified_since: restrict results to those whose status (own, want, etc.) has been changed/added since ``modified_since``. Format: ``YY-MM-DD`` or ``YY-MM-DD HH:MM:SS``


        :return: ``Collection`` object
        :rtype: :py:class:`boardgamegeek.collection.Collection`
        :return: ``None`` if user not found

        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekError` in case of invalid parameters
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIRetryError` if this request should be retried after a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekTimeoutError` if there was a timeout
        """

        # Parameter validation

        if not user_name:
            raise BGGError("no user name specified")

        if subtype not in COLLECTION_SUBTYPES:
            raise BGGError("invalid 'subtype': {}".format(subtype))

        params={"username": user_name,
                "subtype": subtype,
                "stats": 1}

        if exclude_subtype is not None:
            if exclude_subtype not in COLLECTION_SUBTYPES:
                raise BGGError("invalid 'exclude_subtype': {}".format(exclude_subtype))

            if subtype == exclude_subtype:
                raise BGGError("incompatible 'subtype' and 'exclude_subtype'")

            params["excludesubtype"] = exclude_subtype

        if ids is not None:
            params["id"] = ",".join(["{}".format(id_) for id_ in ids])

        for param in ["versions", "own", "rated", "played", "trade", "want", "wishlist", "preordered"]:
            p = locals()[param]
            if p is not None:
                params[param] = 1 if p else 0

        if commented is not None:
            params["comment"] = 1 if commented else 0

        if wishlist_prio is not None:
            if 1 <= wishlist_prio <= 5:
                params["wishlishpriority"] = wishlist_prio
            else:
                raise BGGError("invalid 'wishlist_prio'")

        if want_to_play is not None:
            params["wanttoplay"] = 1 if want_to_play else 0

        if want_to_buy is not None:
            params["wanttobuy"] = 1 if want_to_buy else 0

        if prev_owned is not None:
            params["prevowned"] = 1 if prev_owned else 0

        if has_parts is not None:
            params["hasparts"] = 1 if has_parts else 0

        if want_parts is not None:
            params["wantparts"] = 1 if want_parts else 0

        if min_rating is not None:
            if 1.0 <= min_rating <= 10.0:
                params["minrating"] = min_rating
            else:
                raise BGGError("invalid 'min_rating'")

        if rating is not None:
            if 1.0 <= rating <= 10.0:
                params["rating"] = rating
            else:
                raise BGGError("invalid 'rating'")

        if min_bgg_rating is not None:
            if 1.0 <= min_bgg_rating <= 10.0:
                params["minbggrating"] = min_bgg_rating
            else:
                raise BGGError("invalid 'bgg_min_rating'")

        if bgg_rating is not None:
            if 1.0 <= bgg_rating <= 10.0:
                params["bggrating"] = bgg_rating
            else:
                raise BGGError("invalid 'bgg_rating'")

        if collection_id is not None:
            params["collid"] = collection_id

        if modified_since is not None:
            params["modifiedsince"] = modified_since

        xml_root = request_and_parse_xml(self.requests_session,
                                         self._collection_api_url,
                                         params=params,
                                         timeout=self._timeout,
                                         retries=self._retries,
                                         retry_delay=self._retry_delay)

        try:
            collection = create_collection_from_xml(xml_root, user_name)
        except BGGError as e:
            log.error("error getting collection data: {}".format(e))
            raise

        try:
            add_collection_items_from_xml(collection, xml_root, subtype)
        except BGGError as e:
            log.error("error adding collection items: {}".format(e))
            # TODO: add error/incomplete flag

        return collection

    def search(self, query, search_type=None, exact=False):
        """
        Search for a game

        :param str query: the string to search for
        :param str search_type: list of strings indicating what to search for. Valid contained values are: "rpgitem", "videogame", "boardgame" (default), "boardgameexpansion"
        :param bool exact: if True, try to match the name exactly
        :return: list of ``SearchResult``
        :rtype: list of :py:class:`boardgamegeek.search.SearchResult`

        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekError` in case of invalid query
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIRetryError` if this request should be retried after a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekTimeoutError` if there was a timeout
        """
        if not query:
            raise BGGError("invalid query string")

        if search_type is None:
            search_type = ["boardgame"]

        params = {"query": query}

        if type(search_type) != list:
            warnings.warn("numeric values for the `search_type` parameter will no longer be supported in future versions. See the documentation for details",
                          UserWarning)

            s_type = []

            if search_type:
                if search_type & BoardGameGeekNetworkAPI.SEARCH_BOARD_GAME:
                    s_type.append("boardgame")
                if search_type & BoardGameGeekNetworkAPI.SEARCH_BOARD_GAME_EXPANSION:
                    s_type.append("boardgameexpansion")
                if search_type & BoardGameGeekNetworkAPI.SEARCH_RPG_ITEM:
                    s_type.append("rpgitem")
                if search_type & BoardGameGeekNetworkAPI.SEARCH_VIDEO_GAME:
                    s_type.append("videogame")

            if s_type:
                params["type"] = ",".join(s_type)
        else:
            if search_type:
                for s in search_type:
                    if s not in ["rpgitem", "videogame", "boardgame", "boardgameexpansion"]:
                        raise BGGError("invalid search type: {}".format(search_type))

                params["type"] = ",".join(search_type)

        if exact:
            params["exact"] = 1

        root = request_and_parse_xml(self.requests_session,
                                     self._search_api_url,
                                     params=params,
                                     timeout=self._timeout,
                                     retries=self._retries,
                                     retry_delay=self._retry_delay)

        results = []
        for item in root.findall("item"):
            kwargs = {"id": item.attrib["id"],
                      "name": xml_subelement_attr(item, "name"),
                      "yearpublished": xml_subelement_attr(item,
                                                           "yearpublished",
                                                           default=0,
                                                           convert=int,
                                                           quiet=True),
                      "type": item.attrib["type"]}

            # TODO: move this inside the object
            results.append(SearchResult(kwargs))

        return results


class BoardGameGeek(BoardGameGeekNetworkAPI):
    """
        Python interface for www.boardgamegeek.com's XML API 2.

        Caching for the requests can be used by specifying an URI for the ``cache`` parameter. By default, an in-memory
        cache is used, with sqlite being the other currently supported option.

        :param cache: A :py:class:`boardgamegeek.cache.CacheBackend` object to be used for caching the requests
        :param timeout: Timeout for network operations
        :param retries: Number of retries to perform in case the API returns HTTP 202 (retry) or in case of timeouts
        :param retry_delay: Time to sleep between retries when the API returns HTTP 202 (retry)
        :param disable_ssl: If true, use HTTP instead of HTTPS for calling the BGG API
        :param requests_per_minute: how many requests per minute to allow to go out to BGG (throttle prevention)

        Example usage::

            >>> bgg = BoardGameGeek()
            >>> game = bgg.game("Android: Netrunner")
            >>> game.id
            124742
            >>> bgg_no_cache = BoardGameGeek(cache=CacheBackendNone())
            >>> bgg_sqlite_cache = BoardGameGeek(cache=CacheBackendSqlite(path="/path/to/cache.db", ttl=3600))

    """
    def __init__(self, cache=CacheBackendMemory(ttl=3600), timeout=15, retries=3, retry_delay=5, disable_ssl=False, requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE):

        api_endpoint = "http{}://www.boardgamegeek.com/xmlapi2".format("" if disable_ssl else "s")
        super(BoardGameGeek, self).__init__(api_endpoint=api_endpoint,
                                            cache=cache,
                                            timeout=timeout,
                                            retries=retries,
                                            retry_delay=retry_delay,
                                            requests_per_minute=requests_per_minute)

    def get_game_id(self, name, choose="first"):
        """
        Returns the BGG ID of a game, searching by name

        :param str name: The name of the game to search for
        :param str choose: method of selecting the game by name, when dealing with multiple results. Valid values: "first", "recent" or "best-rank"
        :return: the game's id
        :rtype: integer
        :return: ``None`` if game wasn't found
        :raises: :py:exc:`boardgamegeek.exceptions.BGGError` in case of invalid name
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiRetryError` if this request should be retried after a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BGGApiTimeoutError` if there was a timeout
        """
        return self._get_game_id(name, game_type="boardgame", choose=choose)

    def game(self, name=None, game_id=None, choose="first", versions=False, videos=False, historical=False,
             marketplace=False, comments=False, rating_comments=False, progress=None):
        """
        Get information about a game.

        :param str name: If not None, get information about a game with this name
        :param integer game_id:  If not None, get information about a game with this id
        :param str choose: method of selecting the game by name, when dealing with multiple results.
                           Valid values are : "first", "recent" or "best-rank"
        :param bool versions: include versions information
        :param bool videos: include videos
        :param bool historical: include historical data
        :param bool marketplace: include marketplace data
        :param bool comments: include comments
        :param bool rating_comments: include comments with rating (ignored in favor of ``comments``, if that is true)
        :return: ``BoardGame`` object
        :rtype: :py:class:`boardgamegeek.games.BoardGame`
        :return: ``None`` if the game wasn't found

        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekError` in case of invalid name or game_id
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIRetryError` if this request should be retried after a
                 short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekTimeoutError` if there was a timeout
        """

        if not name and game_id is None:
            raise BGGError("game name or id not specified")

        if game_id is None:
            game_id = self.get_game_id(name, choose=choose)
            if game_id is None:
                log.error("couldn't find any game named '{}'".format(name))
                raise BGGItemNotFoundError

        log.debug("retrieving game id {}{}".format(game_id, " ({})".format(name) if name is not None else ""))

        params = {"id": game_id,
                  "versions": 1 if versions else 0,
                  "videos": 1 if videos else 0,
                  "historical": 1 if historical else 0,
                  "marketplace": 1 if marketplace else 0,
                  "comments": 1 if comments else 0,
                  "ratingcomments": 1 if rating_comments else 0,
                  "pagesize": 100,
                  "page": 1,
                  "stats": 1}

        xml_root = request_and_parse_xml(self.requests_session,
                                         self._thing_api_url,
                                         params=params,
                                         timeout=self._timeout,
                                         retries=self._retries,
                                         retry_delay=self._retry_delay)

        xml_root = xml_root.find("item")
        if xml_root is None:
            msg = "invalid data for game id: {}{}".format(game_id, "" if name is None else " ({})".format(name))
            raise BGGApiError(msg)

        try:
            game = create_game_from_xml(xml_root,
                                        game_id=game_id,
                                        html_parser=html_parser)
        except BGGError as e:
            log.error("error getting game data: {}".format(e))
            raise

        try:
            added_items, total = add_game_comments_from_xml(game, xml_root, comments=comments)
            call_progress_cb(progress, len(game.comments), total)
        except BGGError as e:
            log.error("error adding game comments: {}".format(e))
            return game

        page = 1
        while added_items and len(game.comments) < total:
            page += 1

            try:
                xml_root = request_and_parse_xml(self.requests_session,
                                                 self._thing_api_url,
                                                 params={"id": game_id,
                                                         "pagesize": 100,
                                                         "comments": 1,
                                                         "page": page})
            except:
                break

            try:
                added_items = add_game_comments_from_xml(game, xml_root, comments=comments)
                call_progress_cb(progress, len(game), game.comments)
            except BGGError as e:
                log.error("error adding game comments: {}".format(e))

        return game

    def games(self, name):
        """
        Return a list containing all games with the given name

        :param str name: the name of the game to search for
        :return: list of :py:class:`boardgamegeek.games.BoardGame`
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIRetryError` if this request should be retried after a short delay
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekAPIError` if the response couldn't be parsed
        :raises: :py:exc:`boardgamegeek.exceptions.BoardGameGeekTimeoutError` if there was a timeout
        """
        return [self.game(game_id=s.id)
                for s in self.search(name,
                                     search_type=["boardgame", "boardgameexpansion"],
                                     exact=True)]
