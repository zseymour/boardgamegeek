#!/usr/bin/env python

import requests
import requests_cache
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError as ETParseError
from time import sleep
import sys

if sys.version_info >= (3,):
    import html.parser as hp
else:
    import HTMLParser as hp

import logging

from .game import Game
from .guild import Guild
from .user import User
from .collection import Collection
from .exceptions import BGGApiError

log = logging.getLogger(__name__)
html_parser = hp.HTMLParser()


def xml_subelement_attr(xml_elem, subelement, convert=None, attribute="value"):
    """
    Return the value of <xml_elem><subelement value="THIS" /></xml_elem>
    :param xml_elem:
    :param subelement:
    :param integer: if True, try to convert to int
    :return:
    """
    if xml_elem is None:
        return None

    subel = xml_elem.find(subelement)
    if subel is not None:
        value = subel.attrib.get(attribute)
        if convert:
            value = convert(value)
        return value
    return None


def xml_subelement_attr_list(xml_elem, subelement, convert=None):
    """
    Return the value of multiple <xml_elem><subelement value="THIS" /></xml_elem> as a list
    :param xml_elem:
    :param subelement:
    :param integer: if True, try to convert to int
    :return:
    """
    if xml_elem is None:
        return None

    subel = xml_elem.findall(subelement)
    res = []
    for e in subel:
        value = e.attrib.get("value")
        if convert:
            value = convert(value)
        res.append(value)

    return res


def xml_subelement_text(xml_elem, subelement, convert=None):
    """
    Return the text from the specified subelement
    :param xml_elem:
    :param subelement:
    :param convert:
    :return:
    """
    if xml_elem is None:
        return None

    subel = xml_elem.find(subelement)
    if subel is not None:
        text = subel.text
        if convert:
            text = convert(text)
        return text
    return None


def get_parsed_xml_response(requests_session, url, params=None):
    """
    Returns a parsed XML

    :param url:
    :param params:
    :return:
    """
    try:
        xml = requests_session.get(url, params=params).text

        if sys.version_info >= (3,):
            root_elem = ET.fromstring(xml)
        else:
            utf8_xml = xml.encode("utf-8")
            root_elem = ET.fromstring(utf8_xml)

    except ETParseError as e:
        raise BGGApiError("error decoding BGG API response: {}".format(e))

    except Exception as e:
        raise BGGApiError("error fetching BGG API response: {}".format(e))

    return root_elem


class BGGNAPI(object):

    def __init__(self, api_endpoint, cache=True, **kwargs):
        """

        :param api_endpoint:
        :param cache: Use caching (default True)
        :return:
        """

        if api_endpoint.endswith("/"):
            self.__api_url = api_endpoint + "{}"
        else:
            self.__api_url = api_endpoint + "/{}"

        if cache:
            self.requests_session = requests_cache.core.CachedSession(cache_name=kwargs.get("cache_name", "bggnapi-cache"),
                                                                      backend=kwargs.get("cache_backend", "sqlite"),
                                                                      expire_after=kwargs.get("cache_time", 3600))
        else:
            self.requests_session = requests.Session()

    def fetch_game(self, name, bgid=None, cache=False):

        if bgid is None:
            url = self.__api_url.format("search")
            params = {"query": name, "exact": 1}

            log.debug(u"fetching boardgame by name \"{}\"".format(name))
            root = get_parsed_xml_response(self.requests_session, url, params=params)
            game = root.find("./*[@type='boardgame']")
            if game is None:
                log.warn(u"game not found: {}".format(name))
                return None

            try:
                bgid = int(game.attrib.get("id"))
                if not bgid:
                    log.warning(u"BGGAPI gave us a game without an id: {}".format(name))
                    return None
            except Exception as e:
                log.error("error getting bgid: {}".format(e))
                return None

        log.debug(u"fetching boardgame by BGG id {}".format(bgid))

        url = self.__api_url.format("thing")
        params = {"id": bgid, "stats": 1}

        root = get_parsed_xml_response(self.requests_session, url, params=params)

        # xml is structured like <items blablabla><item>..
        root = root.find("item")

        kwargs = {"id": bgid,
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
                  "publishers": xml_subelement_attr_list(root, ".//link[@type='boardgamepublisher']"),
                  }

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

        return Game(kwargs)

    def fetch_guild(self, gid, forcefetch=False):
        """
        Fetch Guild information from BGG and populate a returned Guild object. There is
        currently no way to query BGG by guild name, it must be by ID.

        BGGAPI always caches the first fetch of a game if given a cachedir. If forcefetch == True,
        fetch_boardgame will overwrite the existing cache if it exists.

        :param gid:
        :param forcefetch:
        :return:
        """
        url = self.__api_url.format("guild")
        params = {"id": gid, "members": 1}

        root = get_parsed_xml_response(self.requests_session, url, params=params)

        if "name" not in root.attrib:
            log.warn(u"Guild {} not yet approved. Unable to get info on it.".format(gid))
            return None

        kwargs = {"name": root.attrib["name"],
                  "gid": gid,
                  "members": []}

        el = root.find(".//members[@count]")
        count = int(el.attrib["count"])
        total_pages = int(2 + (count / 25))   # 25 memebers per page according to BGGAPI
        if total_pages >= 10:
            log.warn("Need to fetch {} pages. It could take awhile.".format(total_pages - 1))

        for page in range(1, total_pages):
            params = {"id": gid, "members": 1, "page": page}

            root = get_parsed_xml_response(self.requests_session, url, params=params)
            if root is None:
                log.warn("Could not get XML for {}".format(url))
                return None

            log.debug("fetched guild page {} of {}".format(page, total_pages))

            for el in root.findall(".//member"):
                kwargs["members"].append(el.attrib["name"])

            if page == 1:
                # grab initial info from first page
                for tag in ["category", "website", "manager"]:
                    kwargs[tag] = xml_subelement_text(root, tag)
                kwargs["description"] = html_parser.unescape(xml_subelement_text(root, "description"))

        return Guild(kwargs)

    def fetch_user(self, name, forcefetch=False):
        url = self.__api_url.format("user")
        params = {"name": name, "hot": 1, "top": 1}

        root = get_parsed_xml_response(self.requests_session, url, params=params)

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

    def fetch_collection(self, name, forcefetch=False):
        params = {"username": name, "stats": 1}
        url = self.__api_url.format("collection")

        # API update: server side cache. fetch will fail until cached, so try a few times.
        retry = 5
        root = None
        found = False

        while retry > 0:
            root = get_parsed_xml_response(self.requests_session, url, params=params)

            # check if there's an error (e.g. invalid username)
            error = root.find(".//error")
            if error is not None:
                raise BGGApiError("API error: {}".format(xml_subelement_text(error, "message")))

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
            raise BGGApiError("failed to get collection after more retries")

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


class BGGAPI(BGGNAPI):
    """
        API for www.boardgamegeek.com
    """
    def __init__(self, cache=True, **kwargs):
        super(BGGAPI, self).__init__(api_endpoint="http://www.boardgamegeek.com/xmlapi2/", cache=cache, **kwargs)