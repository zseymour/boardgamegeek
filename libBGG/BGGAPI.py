#!/usr/bin/env python

# Note: python 2.7
import requests
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError as ETParseError
from time import sleep
import sys

if sys.version_info >= (3,):
    import io as StringIO
else:
    import StringIO

import logging

from libBGG.Boardgame import Boardgame
from libBGG.Guild import Guild
from libBGG.User import User
from libBGG.Collection import Collection, Rating, BoardgameStatus

log = logging.getLogger(__name__)


class BGGAPIException(Exception):
    pass


class BGGAPI(object):
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
    def __init__(self, cache=None):
        self.api_url = "http://www.boardgamegeek.com/xmlapi2/{}"
        self.cache = cache

    def _fetch_tree(self, url, params=None):
        try:
            r = requests.get(url, params=params)

            if sys.version_info >= (3,):
                tree = ET.parse(StringIO.StringIO(r.text))
            else:
                utf8_text = r.text.encode("utf-8")
                tree = ET.parse(StringIO.StringIO(utf8_text))

        except Exception as e:
            log.error("error getting URL {}: {}".format(url, e))
            # raise BGGAPIException(e)
            return None
        except ETParseError as e:
            log.critical("unable to parse BGG response to {}".format(url))
            # raise BGGAPIException(e)
            return None

        return tree

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

            url = self.api_url.format("search")
            params = {"query": name, "exact": 1}

            log.debug(u"fetching boardgame by name \"{}\"".format(name))
            tree = self._fetch_tree(url, params=params)
            game = tree.find("./*[@type='boardgame']")
            if game is None:
                log.warn(u"game not found: {}".format(name))
                return None

            bgid = game.attrib.get("id")
            if not bgid:
                log.warning(u"BGGAPI gave us a game without an id: {}".format(name))
                return None

        log.debug(u"fetching boardgame by BGG ID \"{}\"".format(bgid))

        url = self.api_url.format("thing")
        params = {"id": bgid}
        if forcefetch or self.cache is None:
            tree = self._fetch_tree(url, params=params)
        else:
            tree = self.cache.get_bg(bgid)
            if tree is None:  # cache miss
                tree = self._fetch_tree(url, params=params)

        if tree is None:
            return None

        if self.cache is not None:
            self.cache.cache_bg(tree, bgid)

        root = tree.getroot()

        kwargs = dict()
        kwargs["bgid"] = bgid
        # entries that use attrib["value"].
        value_map = {
            ".//yearpublished": "year",
            ".//minplayers": "minplayers",
            ".//maxplayers": "maxplayers",
            ".//playingtime": "playingtime",
            ".//name": "names",
            ".//link[@type='boardgamefamily']": "families",
            ".//link[@type='boardgamecategory']": "categories",
            ".//link[@type='boardgamemechanic']": "mechanics",
            ".//link[@type='boardgamedesigner']": "designers",
            ".//link[@type='boardgameartist']": "artists",
            ".//link[@type='boardgamepublisher']": "publishers",
        }

        for xpath, bg_arg in value_map.items():
            els = root.findall(xpath)
            for el in els:
                if "value" in el.attrib:
                    if bg_arg in kwargs:
                        # multiple entries, make this arg a list.
                        if type(kwargs[bg_arg]) != list:
                            kwargs[bg_arg] = [kwargs[bg_arg]]
                        kwargs[bg_arg].append(el.attrib["value"])
                    else:
                        kwargs[bg_arg] = el.attrib["value"]
                else:
                    log.warn(u"no \"value\" found in {} for game: {}".format(xpath, name))

        # entries that use text instead of attrib["value"]
        value_map = {
            "./thumbnail": "thumbnail",
            "./image": "image",
            "./description": "description"
        }
        for xpath, bg_arg in value_map.items():
            els = root.findall(xpath)
            if els:
                if len(els) > 0:
                    log.warn("Found multiple entries for {}, ignoring all but first".format(xpath))
                kwargs[bg_arg] = els[0].text

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
        url = self.api_url.format("guild")
        params = {"id": gid, "members": 1}

        if forcefetch == True or self.cache is None:
            tree = self._fetch_tree(url, params=params)
        else:
            tree = self.cache.get_guild(gid)
            if tree is None:  # cache miss
                tree = self._fetch_tree(url, params=params)

        if tree is None:
            log.warn("Could not get XML for {}".format(url))
            return None

        if self.cache is not None:
            self.cache.cache_guild(tree, gid)

        root = tree.getroot()

        if "name" not in root.attrib:
            log.warn(u"Guild {} not yet approved. Unable to get info on it.".format(gid))
            return None

        kwargs = dict()
        kwargs["name"] = root.attrib["name"]
        kwargs["gid"] = gid
        kwargs["members"] = list()

        el = root.find(".//members[@count]")
        count = int(el.attrib["count"])
        total_pages = int(2+(count/25))   # 25 memebers per page according to BGGAPI
        if total_pages >= 10:
            log.warn("Need to fetch {} pages. It could take awhile.".format(total_pages - 1))

        for page in range(1,total_pages):
            url = self.api_url.format("guild")
            params = {"id": gid, "members": 1, "page": page}

            if forcefetch == True or self.cache is None:
                tree = self._fetch_tree(url, params=params)
            else:
                tree = self.cache.get_guild(gid, page=page)
                if tree is None:  # cache miss
                    tree = self._fetch_tree(url, params=params)

            if tree is None:
                log.warn("Could not get XML for {}".format(url))
                return None

            if self.cache is not None:
                self.cache.cache_guild(tree, gid, page=page)

            root = tree.getroot()
            log.debug("fetched guild page {} of {}".format(page, total_pages))

            for el in root.findall(".//member"):
                kwargs["members"].append(el.attrib["name"])

            if page == 1:
                # grab initial info from first page
                for tag in ["description", "category", "website", "manager"]:
                    el = root.find(tag)
                    if not el is None:
                        kwargs[tag] = el.text

        return Guild(**kwargs)

    def fetch_user(self, name, forcefetch=False):
        url = self.api_url.format("user")
        params = {"name": name, "hot": 1, "top": 1}

        if forcefetch == True or self.cache is None:
            tree = self._fetch_tree(url, params=params)
        else:
            tree = self.cache.get_user(name)
            if tree is None:  # cache miss
                tree = self._fetch_tree(url, params=params)

        if tree is None:
            log.warn("Could not get XML for {}".format(url))
            return None

        if self.cache is not None:
            self.cache.cache_user(tree, name)

        root = tree.getroot()

        kwargs = dict()
        kwargs["name"] = root.attrib["name"]
        kwargs["bgid"] = root.attrib["id"]

        value_map = {
            ".//firstname": "firstname",
            ".//lastname": "lastname",
            ".//yearregistered": "yearregistered",
            ".//stateorprovince": "stateorprovince",
            ".//country": "country",
            ".//traderating": "traderating",
        }

        # cut and pasted from fetch_boardgame. TODO put this in separate function.
        for xpath, bg_arg in value_map.items():
            els = root.findall(xpath)
            for el in els:
                if "value" in el.attrib:
                    if bg_arg in kwargs:
                        # multiple entries, make this arg a list.
                        if type(kwargs[bg_arg]) != list:
                            kwargs[bg_arg] = [kwargs[bg_arg]]
                        kwargs[bg_arg].append(el.attrib["value"])
                    else:
                        kwargs[bg_arg] = el.attrib["value"]
                else:
                    log.warn(u"no \"value\" found in {} for user {}".format(xpath, name))

        for xpath, prop in {".//top/item": "top10", ".//hot/item": "hot10"}.items():
            els = root.findall(xpath)   # do we need to sort these by attrib="rank"? If so, how?
            for el in els:
                if not prop in kwargs:
                    kwargs[prop] = list()
                kwargs[prop].append(el.attrib["name"])

        return User(**kwargs)

    def fetch_collection(self, name, forcefetch=False):
        params = {"username": name, "stats": 1}
        url = self.api_url.format("collection")

        if forcefetch == True or self.cache is None:
            # API update: server side cache. fetch will fail until cached, so try a few times.
            retry = 15 
            sleep_time = 2
            while retry != 0:
                tree = self._fetch_tree(url, params=params)
                if not tree:
                    # some fatal error while fetching...
                    break
                els = tree.getroot().findall(".//item[@subtype='boardgame']")
                if len(els) == 0:
                    # TODO: what if collection has 0 games ?
                    log.debug("Found 0 boardgames. Trying again in {} seconds.".format(sleep_time))
                    retry = retry - 1
                    sleep(sleep_time)
                else:
                    log.debug("Found {} boardgames. Continuing with processing.".format(len(els)))
                    break
        else:
            tree = self.cache.get_collection(name)
            # FIXME: need retry here too
            if tree is None:  # cache miss
                tree = self._fetch_tree(url, params=params)

        if tree is None:
            log.warn("Could not get XML for {}".format(url))
            return None

        if self.cache is not None:
            self.cache.cache_collection(tree, name)

        root = tree.getroot()
        collection = Collection(name)

        # build up the games, status, and rating and add to collection.
        els = root.findall(".//item[@subtype='boardgame']")
        log.debug(u"Found {} games in {}\'s collection.".format(len(els), name))
        for el in els:
            stats = el.find("stats")
            rating = stats.find("rating")
            status = el.find("status")

            kwargs = dict()
            bgname = el.find("name").text
            kwargs["names"] = bgname
            bgid = el.attrib["objectid"]
            kwargs["bgid"] = bgid
            subel = el.find("yearpublished")
            kwargs["year"] = subel.text if subel is not None else None
            subel = el.find("image")
            kwargs["image"] = subel.text if subel is not None else None
            subel = el.find("thumbnail")
            kwargs["thumbnail"] = subel.text if subel is not None else None

            for attr in ["minplayers", "maxplayers", "playingtime"]:
                kwargs[attr] = stats.attrib.get(attr, "")

            log.debug("--> KWARG: {}".format(kwargs))
            collection.games.append(Boardgame(**kwargs))
           
            kwargs = dict()
            # this only works as BoardgameStatus.__slots__ matches most of the XML attributes
            # exactly. i.e. this is probably bad idea.
            for prop in BoardgameStatus.__slots__:
                kwargs[prop] = status.attrib.get(prop, "")
            kwargs["numplays"] = el.find("numplays").text
            kwargs["name"] = bgname
            kwargs["bgid"] = bgid
            collection.status[bgname] = BoardgameStatus(**kwargs)

            kwargs = dict()
            kwargs["name"] = bgname
            kwargs["bgid"] = bgid
            if "value" in rating.attrib and rating.attrib["value"] != "N/A":
                kwargs["userrating"] = rating.attrib["value"]
            else:
                kwargs["userrating"] = None

            for prop in Rating.__slots__:
                rate_el = rating.find(prop)
                if not rate_el is None:
                    kwargs[prop] = rate_el.attrib.get("value", "")

            kwargs["BGGrank"] = rating.find("ranks/rank[@name='boardgame']").attrib["value"]
            log.debug(u"{} ranked {} by BGG - rated {} by {}".format(bgname,
                                                                     kwargs["BGGrank"],
                                                                     kwargs["userrating"],
                                                                     name))
            log.debug(u"Creating Rating with: {}".format(kwargs))
            collection.rating[bgid] = Rating(**kwargs)

        return collection
