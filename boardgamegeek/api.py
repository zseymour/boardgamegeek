import logging
import requests
import requests_cache
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
from .exceptions import BoardGameGeekAPIError, BoardGameGeekError
from .utils import xml_subelement_attr, xml_subelement_text, xml_subelement_attr_list, get_parsed_xml_response


log = logging.getLogger("")
html_parser = hp.HTMLParser()


class BGGNAPI(object):

    def __init__(self, api_endpoint, cache=True, **kwargs):
        """

        :param api_endpoint:
        :param cache: Use caching (default True)
        :return:
        """
        self._search_api_url = api_endpoint + "/search"
        self._thing_api_url = api_endpoint + "/thing"
        self._guild_api_url = api_endpoint + "/guild"
        self._user_api_url = api_endpoint + "/user"
        self._collection_api_url = api_endpoint + "/collection"

        if cache:
            cache_args = {"cache_name": kwargs.get("cache_name", "bggnapi-cache"),
                          "backend": kwargs.get("cache_backend", "sqlite"),
                          "expire_after": kwargs.get("cache_time", 3600),
                          "extension": ".cache"}

            if "cache_location" in kwargs:
                cache_args["location"] = kwargs["cache_location"]

            self.requests_session = requests_cache.core.CachedSession(**cache_args)
        else:
            self.requests_session = requests.Session()

    def _get_game_id(self, name, game_type):

        if game_type not in ["rpgitem", "videogame", "boardgame", "boardgameexpansion"]:
            raise BoardGameGeekError("invalid game type: {}".format(game_type))

        params = {"query": name, "exact": 1}

        log.debug(u"fetching game by name \"{}\"".format(name))

        root = get_parsed_xml_response(self.requests_session,
                                       self._search_api_url,
                                       params=params)

        # game_type can be rpgitem, videogame, boardgame, or boardgameexpansion
        game = root.find(".//item[@type='{}']".format(game_type))
        if game is None:
            log.warn(u"game not found: {}".format(name))
            return None

        game_id = int(game.attrib.get("id"))
        if not game_id:
            raise BoardGameGeekAPIError("response didn't contain the game id")

    def guild(self, gid):

        root = get_parsed_xml_response(self.requests_session,
                                       self._guild_api_url,
                                       params={"id": gid, "members": 1})

        if "name" not in root.attrib:
            log.warn(u"unable to get guild information (name not found)".format(gid))
            return None

        kwargs = {"name": root.attrib["name"],
                  "gid": gid,
                  "members": []}

        el = root.find(".//members[@count]")
        count = int(el.attrib["count"])
        total_pages = int(2 + (count / 25))   # 25 memebers per page according to BGGAPI

        for page in range(1, total_pages):
            params = {"id": gid, "members": 1, "page": page}

            root = get_parsed_xml_response(self.requests_session,
                                           self._guild_api_url,
                                           params=params)
            log.debug("fetched guild page {} of {}".format(page, total_pages))

            for el in root.findall(".//member"):
                kwargs["members"].append(el.attrib["name"])

            if page == 1:
                # grab initial info from first page
                for tag in ["category", "website", "manager"]:
                    kwargs[tag] = xml_subelement_text(root, tag)
                kwargs["description"] = html_parser.unescape(xml_subelement_text(root, "description"))

        return Guild(kwargs)

    def user(self, name):

        root = get_parsed_xml_response(self.requests_session,
                                       self._user_api_url,
                                       params={"name": name, "hot": 1, "top": 1})

        kwargs = {"name": root.attrib["name"],
                  "id": int(root.attrib["id"])}

        for i in ["firstname", "lastname", "avatarlink", "lastlogin",
                  "stateorprovince", "country", "webaddress", "xboxaccount",
                  "wiiaccount", "steamaccount", "psnaccount", "traderating"]:
            kwargs[i] = xml_subelement_attr(root, i)

        kwargs["yearregistered"] = xml_subelement_attr(root, "yearregistered", convert=int)

        # FIXME: figure this out, if really wanted.

        # for xpath, prop in {".//top/item": "top10", ".//hot/item": "hot10"}.items():
        #     els = root.findall(xpath)   # do we need to sort these by attrib="rank"? If so, how?
        #     for el in els:
        #         if not prop in kwargs:
        #             kwargs[prop] = list()
        #         kwargs[prop].append(el.attrib["name"])

        return User(kwargs)

    def collection(self, name):
        # API update: server side cache. fetch will fail until cached, so try a few times.
        retry = 5
        root = None
        found = False

        while retry > 0:
            root = get_parsed_xml_response(self.requests_session,
                                           self._collection_api_url,
                                           params={"username": name, "stats": 1})

            # check if there's an error (e.g. invalid username)
            error = root.find(".//error")
            if error is not None:
                raise BoardGameGeekAPIError("API error: {}".format(xml_subelement_text(error, "message")))

            xml_boardgame_elements = root.findall(".//item[@subtype='boardgame']")
            if not len(xml_boardgame_elements):
                # TODO: what if collection has 0 games ?
                log.debug("found 0 boardgames, sleeping")
                retry -= 1
                sleep(5)
            else:
                log.debug("found {} boardgames, continuing with processing.".format(len(xml_boardgame_elements)))
                found = True
                break

        if not found:
            raise BoardGameGeekAPIError("failed to get collection after more retries")

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

            collection.add_game(game)

        return collection


class BoardGameGeek(BGGNAPI):
    """
        API for www.boardgamegeek.com
    """
    def __init__(self, cache=True, **kwargs):
        super(BoardGameGeek, self).__init__(api_endpoint="http://www.boardgamegeek.com/xmlapi2",
                                            cache=cache,
                                            **kwargs)

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

        log.debug(u"retrieving game id {}{}".format(game_id, u" ({})".format(name) if name is not None else ""))

        root = get_parsed_xml_response(self.requests_session,
                                       self._thing_api_url,
                                       params={"id": game_id, "stats": 1})

        # xml is structured like <items blablabla><item>..
        root = root.find("item")

        kwargs = {"id": game_id,
                  "thumbnail": xml_subelement_text(root, "thumbnail"),
                  "image": xml_subelement_text(root, "image"),
                  "description": html_parser.unescape(xml_subelement_text(root, "description")),
                  "families": xml_subelement_attr_list(root, ".//link[@type='boardgamefamily']"),
                  "categories": xml_subelement_attr_list(root, ".//link[@type='boardgamecategory']"),
                  "expansions": xml_subelement_attr_list(root, ".//link[@type='boardgameexpansion']"),
                  "implementations": xml_subelement_attr_list(root, ".//link[@type='boardgameimplementation']"),
                  "mechanics": xml_subelement_attr_list(root, ".//link[@type='boardgamemechanic']"),
                  "designers": xml_subelement_attr_list(root, ".//link[@type='boardgamedesigner']"),
                  "artists": xml_subelement_attr_list(root, ".//link[@type='boardgameartist']"),
                  "publishers": xml_subelement_attr_list(root, ".//link[@type='boardgamepublisher']")}

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