# coding: utf-8

"""
:mod:`boardgamegeek.api` - Core functions
=========================================

This module contains the core functionality needed to retrieve data from boardgamegeek.com and parse it into usable
objects.

.. module:: boardgamegeek.api
   :platform: Unix, Windows
   :synopsis: module handling communication with the online BGG API

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""
from __future__ import unicode_literals

import logging
import requests
import datetime
from time import sleep
import sys

# This is required for decoding HTML entities from the description text
# of games
if sys.version_info >= (3,):
    import html.parser as hp
else:
    import HTMLParser as hp


from .games import BoardGame
from .guild import Guild
from .user import User
from .collection import Collection
from .plays import Plays
from .exceptions import BoardGameGeekAPIError, BoardGameGeekError, BoardGameGeekAPIRetryError, BoardGameGeekAPINonXMLError
from .utils import xml_subelement_attr, xml_subelement_text, xml_subelement_attr_list, get_parsed_xml_response
from .utils import get_cache_session_from_uri


log = logging.getLogger("boardgamegeek.api")
html_parser = hp.HTMLParser()


class BoardGameGeekNetworkAPI(object):
    COLLECTION_FETCH_RETRIES = 5
    COLLECTION_FETCH_DELAY = 5
    GUILD_MEMBERS_PER_PAGE = 25         # how many guild members are per page when listing guild members
    USER_GUILD_BUDDIES_PER_PAGE = 100   # how many buddies/guilds are per page when retrieving user info

    def __init__(self, api_endpoint, cache=None, timeout=5):

        self._search_api_url = api_endpoint + "/search"
        self._thing_api_url = api_endpoint + "/thing"
        self._guild_api_url = api_endpoint + "/guild"
        self._user_api_url = api_endpoint + "/user"
        self._plays_api_url = api_endpoint + "/plays"
        self._collection_api_url = api_endpoint + "/collection"
        self._timeout = timeout

        if cache:
            self.requests_session = get_cache_session_from_uri(cache)
        else:
            self.requests_session = requests.Session()

    def _get_game_id(self, name, game_type):

        if game_type not in ["rpgitem", "videogame", "boardgame", "boardgameexpansion"]:
            raise BoardGameGeekError("invalid game type: {}".format(game_type))

        log.debug("getting game id of '{}'".format(name))

        root = get_parsed_xml_response(self.requests_session,
                                       self._search_api_url,
                                       params={"query": name, "exact": 1},
                                       timeout=self._timeout)

        # game_type can be rpgitem, videogame, boardgame, or boardgameexpansion
        game = root.find(".//item[@type='{}']".format(game_type))
        if game is None:
            log.warn("game not found: {}".format(name))
            return None

        game_id = int(game.attrib.get("id"))
        if not game_id:
            raise BoardGameGeekAPIError("response didn't contain the game id")
        return game_id

    def guild(self, guild_id, progress=None):
        """
        Retrieves details about a guild

        :param guild_id: The ID of the guild
        :param progress: Optional progress callback for member fetching
        :return: a Guild object containing the details
        """

        try:
            guild_id = int(guild_id)
        except:
            raise BoardGameGeekError("invalid guild id")

        root = get_parsed_xml_response(self.requests_session,
                                       self._guild_api_url,
                                       params={"id": guild_id, "members": 1},
                                       timeout=self._timeout)

        if "name" not in root.attrib:
            log.warn("unable to get guild information (name not found)".format(guild_id))
            return None

        kwargs = {"name": root.attrib["name"],
                  "created": root.attrib.get("created"),
                  "id": guild_id,
                  "members": []}

        # grab initial info from first page
        for tag in ["category", "website", "manager"]:
            kwargs[tag] = xml_subelement_text(root, tag)

        description = xml_subelement_text(root, "description")
        if description is not None:
            kwargs["description"] = html_parser.unescape(description)
        else:
            kwargs["description"] = None

        # Grab location info
        location = root.find("location")
        if location is not None:
            kwargs["city"] = xml_subelement_text(location, "city")
            kwargs["country"] = xml_subelement_text(location, "country")
            kwargs["postalcode"] = xml_subelement_text(location, "postalcode")
            kwargs["addr1"] = xml_subelement_text(location, "addr1")
            kwargs["addr2"] = xml_subelement_text(location, "addr2")
            kwargs["stateorprovince"] = xml_subelement_text(location, "stateorprovince")

        el = root.find(".//members[@count]")
        count = int(el.attrib["count"])

        # first page of members has already been retrieved with the initial call
        for el in root.findall(".//member"):
            kwargs["members"].append(el.attrib["name"])

        def _call_progress_cb():
            if progress is not None:
                progress(len(kwargs["members"]), count)

        _call_progress_cb()

        page = 2

        while len(kwargs["members"]) < count:
            added_member = False
            log.debug("fetching page {}".format(page))
            root = get_parsed_xml_response(self.requests_session,
                                           self._guild_api_url,
                                           params={"id": guild_id, "members": 1, "page": page},
                                           timeout=self._timeout)

            for el in root.findall(".//member"):
                kwargs["members"].append(el.attrib["name"])
                added_member = True

            _call_progress_cb()

            page += 1
            if not added_member:
                # didn't add anything anymore? break
                break

        return Guild(kwargs)

    def user(self, name, progress=None):
        """
        Retrieves details about an user

        :param name: user's login name
        :return:
        """

        if not name:
            raise BoardGameGeekError("no user name specified")

        params = {"name": name, "buddies": 1, "guilds": 1, "hot": 1, "top": 1}

        try:
            root = get_parsed_xml_response(self.requests_session,
                                           self._user_api_url,
                                           params=params,
                                           timeout=self._timeout)
        except BoardGameGeekAPINonXMLError:
            # if the api doesn't return XML, assume the user wasn't found
            return None

        # when the user is not found, the API returns an response, but with most fields empty. id is empty too
        try:
            kwargs = {"name": root.attrib["name"],
                      "id": int(root.attrib["id"])}
        except:
            return None

        for i in ["firstname", "lastname", "avatarlink",
                  "stateorprovince", "country", "webaddress", "xboxaccount",
                  "wiiaccount", "steamaccount", "psnaccount", "traderating"]:
            kwargs[i] = xml_subelement_attr(root, i)

        kwargs["lastlogin"] = xml_subelement_attr(root,
                                                  "lastlogin",
                                                  convert=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))

        kwargs["yearregistered"] = xml_subelement_attr(root, "yearregistered", convert=int)

        user = User(kwargs)

        # add top items
        for top_item in root.findall(".//top/item"):
            user._add_top_item({"id": int(top_item.attrib["id"]),
                                "name": top_item.attrib["name"]})

        # add hot items
        for hot_item in root.findall(".//hot/item"):
            user._add_hot_item({"id": int(hot_item.attrib["id"]),
                                "name": hot_item.attrib["name"]})

        total_buddies = 0
        total_guilds = 0

        buddies = root.find("buddies")
        if buddies is not None:
            total_buddies = int(buddies.attrib["total"])
            if total_buddies > 0:
                # add the buddies from the first page
                for buddy in buddies.findall(".//buddy"):
                    user._add_buddy({"name": buddy.attrib["name"],
                                    "id": buddy.attrib["id"]})

        guilds = root.find("guilds")
        if guilds is not None:
            total_guilds = int(guilds.attrib["total"])
            if total_guilds > 0:
                # add the guilds from the first page
                for guild in guilds.findall(".//guild"):
                    user._add_guild({"name": guild.attrib["name"],
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
            root = get_parsed_xml_response(self.requests_session,
                                           self._user_api_url,
                                           params=params,
                                           timeout=self._timeout)

            for buddy in root.findall(".//buddy"):
                user._add_buddy({"name": buddy.attrib["name"],
                                "id": buddy.attrib["id"]})
                added_buddy = True

            for guild in root.findall(".//guild"):
                user._add_guild({"name": guild.attrib["name"],
                                "id": guild.attrib["id"]})
                added_guild = True

            _call_progress_cb()
            page += 1

            if not added_buddy and not added_guild:
                log.debug("didn't add any buddy/guild after fetching page {}, stopping here".format(page))
                break

        return user

    def plays(self, name=None, game_id=None, progress=None):
        """
        Retrieves the user's play list

        :param name: user name to retrieve the plays for
        :param game_id: game id to retrieve the plays for
        :return: :class:`Plays` object containing all the plays
        :raises: :class:`BoardGameGeekError` on errors

        """
        if not name and not game_id:
            raise BoardGameGeekError("no user name specified")

        if name and game_id:
            raise BoardGameGeekError("can't retrieve by user and by game at the same time")

        if name:
            params = {"username": name}
        else:
            try:
                params = {"id": int(game_id)}
            except:
                raise BoardGameGeekError("invalid game id")

        try:
            root = get_parsed_xml_response(self.requests_session,
                                           self._plays_api_url,
                                           params=params,
                                           timeout=self._timeout)
        except Exception as e:
            # The API seems to return HTML in case of an invalid username.
            # just return None for the time being.
            log.error("error trying to fetch plays: {}".format(e))
            return None

        count = int(root.attrib["total"])   # how many plays

        if name:
            plays = Plays({"username": root.attrib["username"],
                           "user_id": int(root.attrib["userid"])})
        else:
            plays = Plays({"game_id": game_id})

        def _add_plays(plays, root):
            added_plays = False
            for play in root.findall(".//play"):
                added_plays = True

                # if we're listing plays by game, each <play> has an userid. If this isn't set, we must be listing
                # an user's collection, thus set it from plays.user_id
                userid = int(play.attrib.get("userid", plays.user_id))

                # TODO: add the game subtype too
                kwargs = {"id": int(play.attrib["id"]),
                          "date": datetime.datetime.strptime(play.attrib["date"], "%Y-%m-%d"),
                          "quantity": int(play.attrib["quantity"]),
                          "duration": int(play.attrib["length"]),
                          "incomplete": int(play.attrib["incomplete"]),
                          "nowinstats": int(play.attrib["nowinstats"]),
                          "user_id": userid,
                          "game_id": xml_subelement_attr(play, "item", attribute="objectid", convert=int),
                          "game_name": xml_subelement_attr(play, "item", attribute="name"),
                          "comment": xml_subelement_text(play, "comments")}
                plays._add_play(kwargs)
            return added_plays

        _add_plays(plays, root)

        def _call_progress_cb():
            if progress is not None:
                progress(len(plays), count)

        _call_progress_cb()

        page = 2
        while len(plays) < count:
            log.debug("fetching page {} of plays".format(page))

            params["page"] = page

            # fetch the next pages of plays
            root = get_parsed_xml_response(self.requests_session,
                                           self._plays_api_url,
                                           params=params,
                                           timeout=self._timeout)

            if not _add_plays(plays, root):
                break

            page += 1
            _call_progress_cb()

        return plays

    def collection(self, name):
        """
        Returns the user's game collection

        :param name: user name to retrieve the collection for
        :return: :class:`Collection` or ``None`` if user not found
        :raises: :class:`BoardGameGeekAPIError` if there was a problem getting the collection
        :raises: :class:`BoardGameGeekError` in case of invalid parameters
        """
        if not name:
            raise BoardGameGeekError("no user name specified")

        retry = BoardGameGeekNetworkAPI.COLLECTION_FETCH_RETRIES
        root = None
        found = False

        while retry > 0:
            try:
                root = get_parsed_xml_response(self.requests_session,
                                               self._collection_api_url,
                                               params={"username": name, "stats": 1},
                                               timeout=self._timeout)
                found = True
                break
            except BoardGameGeekAPIRetryError:
                retry -= 1
                sleep(BoardGameGeekNetworkAPI.COLLECTION_FETCH_DELAY)
                log.debug("retrying collection fetch")
                continue

        if not found:
            raise BoardGameGeekAPIError("failed to get {}'s collection after multiple retries".format(name))

        # check if there's an error (e.g. invalid username)
        error = root.find(".//error")
        if error is not None:
            message = xml_subelement_text(error, "message")
            log.error("error fetching collection for {}: {}".format(name, message))
            return None

        collection = Collection({"owner": name, "items": []})

        # search for all boardgames in the collection, add them to the list
        for xml_el in root.findall(".//item[@subtype='boardgame']"):
            # get the user's rating for this game in his collection
            stats = xml_el.find("stats")
            rating = xml_subelement_attr(stats, "rating")
            try:
                rating = float(rating)
            except:
                rating = None

            # name and id of the game in collection
            game = {"name": xml_subelement_text(xml_el, "name"),
                    "id": int(xml_el.attrib.get("objectid")),
                    "rating": rating}

            status = xml_el.find("status")
            game.update({stat: status.attrib.get(stat) for stat in ["lastmodified",
                                                                    "own",
                                                                    "preordered",
                                                                    "prevowned",
                                                                    "want",
                                                                    "wanttobuy",
                                                                    "wanttoplay",
                                                                    "fortrade",
                                                                    "wishlist",
                                                                    "wishlistpriority"]})

            collection._add_game(game)

        return collection


class BoardGameGeek(BoardGameGeekNetworkAPI):
    """
        Pyhton interface for www.boardgamegeek.com's XML API.

        Caching for the requests can be used by specifying an URI for the ``cache`` parameter. By default, an in-memory
        cache is used, with "sqlite" being the other currently supported option.

        Example usage::

            >>> bgg = BoardGameGeek()
            >>> game = bgg.game("Android: Netrunner")
            >>> game.id
            124742
            >>> bgg_no_cache = BoardGameGeek(cache=None)
            >>> bgg_sqlite_cache = BoardGameGeek(cache="sqlite:///path/to/cache.db?ttl=3600")

    """
    def __init__(self, cache="memory:///?ttl=3600"):
        super(BoardGameGeek, self).__init__(api_endpoint="http://www.boardgamegeek.com/xmlapi2", cache=cache)

    def get_game_id(self, name):
        return self._get_game_id(name, "boardgame")

    def game(self, name=None, game_id=None):

        if not name and game_id is None:
            raise BoardGameGeekError("game name or id not specified")

        if game_id is None:
            game_id = self.get_game_id(name)
            if game_id is None:
                log.error("couldn't find any game named '{}'".format(name))
                return None

        log.debug("retrieving game id {}{}".format(game_id, " ({})".format(name) if name is not None else ""))

        root = get_parsed_xml_response(self.requests_session,
                                       self._thing_api_url,
                                       params={"id": game_id, "stats": 1},
                                       timeout=self._timeout)

        # xml is structured like <items blablabla><item>..
        root = root.find("item")
        if root is None:
            msg = "error parsing game data for game id: {}{}".format(game_id,
                                                                      " ({})".format(name) if name is not None else "")
            raise BoardGameGeekAPIError(msg)

        kwargs = {"id": game_id,
                  "thumbnail": xml_subelement_text(root, "thumbnail"),
                  "image": xml_subelement_text(root, "image"),
                  "families": xml_subelement_attr_list(root, ".//link[@type='boardgamefamily']"),
                  "categories": xml_subelement_attr_list(root, ".//link[@type='boardgamecategory']"),
                  "expansions": xml_subelement_attr_list(root, ".//link[@type='boardgameexpansion']"),
                  "implementations": xml_subelement_attr_list(root, ".//link[@type='boardgameimplementation']"),
                  "mechanics": xml_subelement_attr_list(root, ".//link[@type='boardgamemechanic']"),
                  "designers": xml_subelement_attr_list(root, ".//link[@type='boardgamedesigner']"),
                  "artists": xml_subelement_attr_list(root, ".//link[@type='boardgameartist']"),
                  "publishers": xml_subelement_attr_list(root, ".//link[@type='boardgamepublisher']")}

        description = xml_subelement_text(root, "description")
        if description is not None:
            kwargs["description"] = html_parser.unescape(description)
        else:
            kwargs["description"] = None

        # These XML elements have a numberic value, attempt to convert them to integers
        for i in ["yearpublished", "minplayers", "maxplayers", "playingtime", "minage"]:
            kwargs[i] = xml_subelement_attr(root, i, convert=int)

        # What's the name of the game :P
        kwargs["name"] = xml_subelement_attr(root, ".//name[@type='primary']")

        # Get alternative names too
        kwargs["alternative_names"] = xml_subelement_attr_list(root, ".//name[@type='alternate']")

        # look for statistics info
        stats = root.find(".//ratings")
        kwargs.update({
            "usersrated": xml_subelement_attr(stats, "usersrated", convert=int),
            "average": xml_subelement_attr(stats, "average", convert=float),
            "bayesaverage": xml_subelement_attr(stats, "bayesaverage", convert=float),
            "stddev": xml_subelement_attr(stats, "stddev", convert=float),
            "median": xml_subelement_attr(stats, "median", convert=float),
            "owned": xml_subelement_attr(stats, "owned", convert=int),
            "trading": xml_subelement_attr(stats, "trading", convert=int),
            "wanting": xml_subelement_attr(stats, "wanting", convert=int),
            "wishing": xml_subelement_attr(stats, "wishing", convert=int),
            "numcomments": xml_subelement_attr(stats, "numcomments", convert=int),
            "numweights": xml_subelement_attr(stats, "numweights", convert=int),
            "averageweight": xml_subelement_attr(stats, "averageweight", convert=float)
        })

        kwargs["ranks"] = []
        ranks = root.findall(".//rank")
        for rank in ranks:
            try:
                rank_value = int(rank.attrib.get("value"))
            except:
                rank_value = None
            kwargs["ranks"].append({"name": rank.attrib.get("name"),
                                    "friendlyname": rank.attrib.get("friendlyname"),
                                    "value": rank_value})

        return BoardGame(kwargs)