#!/usr/bin/env python

import requests
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError as ETParseError
from time import sleep
import sys

import logging

from libBGG.Boardgame import Boardgame
from libBGG.Guild import Guild
from libBGG.User import User
from libBGG.Collection import Collection, Rating, BoardgameStatus
from .exceptions import BGGApiError

log = logging.getLogger(__name__)


def xml_subelement_attr(xml_elem, subelement, convert=None, attribute="value"):
    """
    Return the value of <xml_elem><subelement value="THIS" /></xml_elem>
    :param xml_elem:
    :param subelement:
    :param integer: if True, try to convert to int
    :return:
    """
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
    subel = xml_elem.find(subelement)
    if subel is not None:
        text = subel.text
        if convert:
            text = convert(text)
        return text
    return None


def fetch_url(url, params=None):
    # using a function for getting the XML from an URL so that we can easily cache the results
    try:
        r = requests.get(url, params=params)
        return r.text
    except Exception as e:
        log.error("error fetching URL {} (params: {}): {}".format(url, params, e))
        raise


def get_parsed_xml_response(url, params=None):
    """
    Returns a parsed XML

    :param url:
    :param params:
    :return:
    """
    try:
        xml = fetch_url(url, params)

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
    """
    BGGAPI is a class that knows how to contact BGG for information, parse out relevant details,
    the create a Python BGG object for general use.

    Example:
        api = BGGAPI()

        bg = api.fetch_boardgame("yinsh")
        print "Yinsh was created in %s by %s" % (bg.year, ", ".join(bg.designers))

        guild = api.fetch("1920")  # BGG only supports fetch by ID.
        print "BGG Guild %s has %d members." % (guild.name, len(guild.members))
    """
    def __init__(self, api_endpoint):

        if api_endpoint.endswith("/"):
            self.__api_url = api_endpoint + "{}"
        else:
            self.__api_url = api_endpoint + "/{}"

    def fetch_boardgame(self, name, bgid=None, forcefetch=False):
        """
        Fetch information about a bardgame from BGG by name. If bgid is given,
        it will be used instead. bgid is the ID of the game at BGG. bgid should be type str.

        BGGAPI always caches the first fetch of a game if given a cachedir. If forcefetch == True,
        fetch_boardgame will fetch or re-fetch from BGG.

        :param name:
        :param bgid:
        :param forcefetch:
        :return:
        """
        if bgid is None:
            # ideally we'd search the cache by name, but that would be
            # difficult. So we just fetch it via BGG.

            url = self.__api_url.format("search")
            params = {"query": name, "exact": 1}

            log.debug(u"fetching boardgame by name \"{}\"".format(name))
            root = get_parsed_xml_response(url, params=params)
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
        params = {"id": bgid}

        root = get_parsed_xml_response(url, params=params)
        if root is None:
            return None

        # xml is structured like <items blablabla><item>..
        root = root.find("item")

        kwargs = {"bgid": bgid,
                  "thumbnail": xml_subelement_text(root, "thumbnail"),
                  "image": xml_subelement_text(root, "image"),
                  "description": xml_subelement_text(root, "description"),
                  "families": xml_subelement_attr_list(root, ".//link[@type='boardgamefamily']"),
                  "categories": xml_subelement_attr_list(root, ".//link[@type='boardgamecategory']"),
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

        log.debug(u"creating boardgame with kwargs: {}".format(kwargs))
        return Boardgame(**kwargs)

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

        root = get_parsed_xml_response(url, params=params)
        if root is None:
            log.warn("Could not get XML for {}".format(url))
            return None

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

            root = get_parsed_xml_response(url, params=params)
            if root is None:
                log.warn("Could not get XML for {}".format(url))
                return None

            log.debug("fetched guild page {} of {}".format(page, total_pages))

            for el in root.findall(".//member"):
                kwargs["members"].append(el.attrib["name"])

            if page == 1:
                # grab initial info from first page
                for tag in ["description", "category", "website", "manager"]:
                    kwargs[tag] = xml_subelement_text(root, tag)

        return Guild(**kwargs)

    def fetch_user(self, name, forcefetch=False):
        url = self.__api_url.format("user")
        params = {"name": name, "hot": 1, "top": 1}

        root = get_parsed_xml_response(url, params=params)
        if root is None:
            log.warn("Could not get XML for {}".format(url))
            return None

        kwargs = {"name": root.attrib["name"],
                  "bgid": int(root.attrib["id"])}

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

        return User(**kwargs)

    def fetch_collection(self, name, forcefetch=False):
        params = {"username": name, "stats": 1}
        url = self.__api_url.format("collection")

        # API update: server side cache. fetch will fail until cached, so try a few times.
        retry = 15
        root = None
        found = False

        while retry > 0:
            root = get_parsed_xml_response(url, params=params)

            els = root.findall(".//item[@subtype='boardgame']")
            if not len(els):
                # TODO: what if collection has 0 games ?
                log.debug("found 0 boardgames, sleeping")
                retry -= 1
                sleep(5)
            else:
                log.debug("found {} boardgames, continuing with processing.".format(len(els)))
                found = True
                break

        if not found:
            raise BGGApiError("failed to get collection after more retries")

        collection = Collection(name)

        # build up the games, status, and rating and add to collection.
        els = root.findall(".//item[@subtype='boardgame']")
        log.debug(u"Found {} games in {}\'s collection.".format(len(els), name))
        
        for el in els:
            stats = el.find("stats")
            rating = stats.find("rating")
            status = el.find("status")

            bgname = el.find("name").text
            bgid = el.attrib["objectid"]

            kwargs = {"names": bgname,
                      "bgid": bgid,
                      "minplayers": xml_subelement_attr(stats, "minplayers", convert=int),
                      "maxplayers": xml_subelement_attr(stats, "maxplayers", convert=int),
                      "playingtime": xml_subelement_attr(stats, "playingtime", convert=int),
                      "year": xml_subelement_text(el, "yearpublished", convert=int),
                      "image": xml_subelement_text(el, "image"),
                      "thumbnail": xml_subelement_text(el, "thumbnail")}

            collection.add_boardgame(Boardgame(**kwargs))

            #
            # Status stuff
            #

            kwargs = {stat: status.attrib.get(stat) for stat in ["lastmodified",
                                                                 "own",
                                                                 "preordered",
                                                                 "prevowned",
                                                                 "want",
                                                                 "wanttobuy",
                                                                 "wanttoplay",
                                                                 "fortrade",
                                                                 "wanttobuy",
                                                                 "wishlist",
                                                                 "wishlistpriority"]}

            kwargs.update({
                "name": bgname,
                "bgid": bgid,
                "numplays": xml_subelement_text(el, "numplays", convert=int)
            })

            collection.add_boardgame_status(bgname, BoardgameStatus(**kwargs))

            kwargs = {"name": bgname,
                      "bgid": bgid,
                      "usersrated": xml_subelement_attr(rating, "usersrated", convert=int),
                      "average": xml_subelement_attr(rating, "average", convert=float),
                      "stddev": xml_subelement_attr(rating, "stddev", convert=float),
                      "bayesaverage": xml_subelement_attr(rating, "bayesaverage", convert=float),
                      "median": xml_subelement_attr(rating, "median", convert=float),
                      "ranks": {}
            }

            ranks = rating.find("ranks")

            if ranks is not None:
                for subel in ranks.findall("rank"):
                    if "name" in subel.attrib:
                        kwargs["ranks"][subel.attrib["name"]] = {
                            "bayesaverage": subel.attrib.get("bayesaverage"),
                            "friendlyname": subel.attrib.get("friendlyname"),
                            "type": subel.attrib.get("type"),
                            "name": subel.attrib["name"],
                            "value": subel.attrib.get("value")
                        }

            user_rating = rating.attrib.get("value")
            kwargs["userrating"] = user_rating if user_rating != "N/A" else None

            collection.add_boardgame_rating(bgname, Rating(**kwargs))

        return collection


class BGGAPI(BGGNAPI):
    """
        API for www.boardgamegeek.com
    """
    def __init__(self):
        super(BGGAPI, self).__init__(api_endpoint="http://www.boardgamegeek.com/xmlapi2/")