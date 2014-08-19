# coding: utf-8

"""
.. module:: boardgamegeek.api
   :platform: Unix, Windows
   :synopsis: module handling communication with the online BGG API

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""
from __future__ import unicode_literals

import logging
import requests
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
from .exceptions import BoardGameGeekAPIError, BoardGameGeekError, BoardGameGeekAPIRetryError
from .utils import xml_subelement_attr, xml_subelement_text, xml_subelement_attr_list, get_parsed_xml_response
from .utils import get_cache_session_from_uri


log = logging.getLogger("boardgamegeek.api")
html_parser = hp.HTMLParser()


class BoardGameGeekNetworkAPI(object):
    COLLECTION_FETCH_RETRIES = 5
    COLLECTION_FETCH_DELAY = 5
    GUILD_MEMBERS_PER_PAGE = 25         # how many guild members are per page when listing guild members
    USER_GUILD_BUDDIES_PER_PAGE = 100   # how many buddies/guilds are per page when retrieving user info

    def __init__(self, api_endpoint, cache=None):

        self._search_api_url = api_endpoint + "/search"
        self._thing_api_url = api_endpoint + "/thing"
        self._guild_api_url = api_endpoint + "/guild"
        self._user_api_url = api_endpoint + "/user"
        self._collection_api_url = api_endpoint + "/collection"

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
                                       params={"query": name, "exact": 1})

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
        root = get_parsed_xml_response(self.requests_session,
                                       self._guild_api_url,
                                       params={"id": guild_id, "members": 1})

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

        # add 1 to the division because in python the result is an integer,
        # rounded down.
        total_pages = 1 + count // BoardGameGeekNetworkAPI.GUILD_MEMBERS_PER_PAGE

        log.debug("there are {} members in this guild => {} pages".format(count, total_pages))

        # first page of members has already been retrieved with the initial call
        for el in root.findall(".//member"):
            kwargs["members"].append(el.attrib["name"])

        if progress is not None:
            progress(len(kwargs["members"]), count)

        # continue from page #2 up to total_pages + 1, since pages on BGG start from 1
        for page in range(2, total_pages + 1):
            log.debug("fetching page {} of {}".format(page, total_pages))
            root = get_parsed_xml_response(self.requests_session,
                                           self._guild_api_url,
                                           params={"id": guild_id, "members": 1, "page": page})

            for el in root.findall(".//member"):
                kwargs["members"].append(el.attrib["name"])

            if progress is not None:
                progress(len(kwargs["members"]), count)

        return Guild(kwargs)

    def user(self, name, progress=None):
        """
        Retrieves details about an user

        :param name: user's login name
        :return:
        """

        root = get_parsed_xml_response(self.requests_session,
                                       self._user_api_url,
                                       params={"name": name, "buddies": 1, "guilds": 1})

        # when the user is not found, the API returns an response, but with most fields empty. id is empty too
        try:
            kwargs = {"name": root.attrib["name"],
                      "id": int(root.attrib["id"])}
        except:
            raise BoardGameGeekError("invalid user name")

        for i in ["firstname", "lastname", "avatarlink", "lastlogin",
                  "stateorprovince", "country", "webaddress", "xboxaccount",
                  "wiiaccount", "steamaccount", "psnaccount", "traderating"]:
            kwargs[i] = xml_subelement_attr(root, i)

        kwargs["yearregistered"] = xml_subelement_attr(root, "yearregistered", convert=int)

        user = User(kwargs)

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

        # determine how many pages we should fetch in order to retrieve a complete buddy/guild list
        max_items_to_fetch = max(total_buddies, total_guilds)
        total_pages = 1 + max_items_to_fetch // BoardGameGeekNetworkAPI.USER_GUILD_BUDDIES_PER_PAGE

        def _progress_cb():
            if progress is not None:
                progress(max(user.total_buddies, user.total_guilds), max_items_to_fetch)

        _progress_cb()

        # repeat the API call and retrieve everything
        for page in range(2, total_pages + 1):
            root = get_parsed_xml_response(self.requests_session,
                                           self._user_api_url,
                                           params={"name": name, "buddies": 1, "guilds": 1, "page": page})

            for buddy in root.findall(".//buddy"):
                user._add_buddy({"name": buddy.attrib["name"],
                                "id": buddy.attrib["id"]})

            for guild in root.findall(".//guild"):
                user._add_guild({"name": guild.attrib["name"],
                                "id": guild.attrib["id"]})

            _progress_cb()

        return user

    def collection(self, name):
        retry = BoardGameGeekNetworkAPI.COLLECTION_FETCH_RETRIES
        root = None
        found = False

        while retry > 0:
            try:
                root = get_parsed_xml_response(self.requests_session,
                                               self._collection_api_url,
                                               params={"username": name, "stats": 1})
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
            raise BoardGameGeekAPIError("API error: {}".format(xml_subelement_text(error, "message")))

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

        if name is None and game_id is None:
            raise BoardGameGeekError("game name or id not specified")

        if game_id is None:
            game_id = self.get_game_id(name)
            if game_id is None:
                log.error("couldn't find any game named '{}'".format(name))
                return None

        log.debug("retrieving game id {}{}".format(game_id, " ({})".format(name) if name is not None else ""))

        root = get_parsed_xml_response(self.requests_session,
                                       self._thing_api_url,
                                       params={"id": game_id, "stats": 1})

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