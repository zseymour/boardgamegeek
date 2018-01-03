# coding: utf-8

import logging
import pytest
import xml.etree.ElementTree as ET


from boardgamegeek import BGGClient, CacheBackendNone


# Kinda hard to test without having a "test" user
TEST_VALID_USER = "fagentu007"
TEST_VALID_USER_ID = 818216
TEST_USER_WITH_LOTS_OF_FRIENDS = "Solamar"        # user chosen randomly (..after a long search :)) ), just needed
                                                  # someone with lots of friends :D
TEST_INVALID_USER = "someOneThatHopefullyWontExistPlsGuysDontCreateThisUser"
TEST_INVALID_GAME_NAME = "blablablathisgamewonteverexist"
TEST_GAME_NAME = "Agricola"
TEST_GAME_ID = 31260

#TEST_GAME_NAME_2 = "Merchant of Venus (second edition)"
#TEST_GAME_ID_2 = 131646

TEST_GAME_NAME_2 = "Advanced Third Reich"
TEST_GAME_ID_2 = 283

TEST_GUILD_ID = 1229
TEST_GUILD_ID_2 = 930

TEST_GAME_ACCESSORY_ID = 104163 # Descent: Journeys in the Dark (second edition) – Conversion Kit

# The URLs when we call the various BGG commands
BGG_COLLECTION_URL = "https://www.boardgamegeek.com/xmlapi2/collection"
BGG_SEARCH_URL = "https://www.boardgamegeek.com/xmlapi2/search"
BGG_THING_URL = "https://www.boardgamegeek.com/xmlapi2/thing"

# The files containing the responses for certain queries
INVALID_REQUEST_XML_FILENAME = "test/Invalid.xml"

AGRICOLA_XML_FILENAME = "test/Agricola.xml"
AGRICOLA_AND_ADVANCED_THIRD_REICH_XML_FILENAME = "test/Agricola+AdvancedThirdReich.xml"
COUP_1653_XML_FILENAME = "test/Coup-1653.xml"
COUP_2088_XML_FILENAME = "test/Coup-2088.xml"
COUP_131357_XML_FILENAME = "test/Coup-131357.xml"
DESCENT_CONVERSION_KIT_XML_FILENAME = "test/DescentConversionKit.xml"
ECLIPSE_11542_XML_FILENAME = "test/Eclipse-11542.xml"
ECLIPSE_23272_XML_FILENAME = "test/Eclipse-23272.xml"
ECLIPSE_72125_XML_FILENAME = "test/Eclipse-72125.xml"
HIJARA_XML_FILENAME = "test/Hijara.xml"
TRIO_XML_FILENAME = "test/Trio.xml"

SEARCH_AGRICOLA_XML_FILENAME = "test/search-Agricola.xml"
SEARCH_COUP_XML_FILENAME = "test/search-Coup.xml"
SEARCH_ECLIPSE_XML_FILENAME = "test/search-Eclipse.xml"

INVALID_COLLECTION_XML_FILENAME = "test/InvalidCollection.xml"
FAGENTU007_XML_FILENAME = "test/fagentu007.xml"


@pytest.fixture
def xml():
    xml_code = """
    <root>
        <node1 attr="hello1" int_attr="1">text</node1>
        <node2 attr="hello2" int_attr="2" />
        <list>
            <li attr="elem1" int_attr="1" />
            <li attr="elem2" int_attr="2" />
            <li attr="elem3" int_attr="3" />
            <li attr="elem4" int_attr="4" />
        </list>
    </root>
    """
    return ET.fromstring(xml_code)


@pytest.fixture
def bgg():
    return BGGClient(cache=CacheBackendNone(), retries=2, retry_delay=1)


@pytest.fixture
def null_logger():
    # create logger
    logger = logging.getLogger("null")
    logger.setLevel(logging.ERROR)
    return logger

class MockResponse():
    """
    A simple object which contains all the fields we need from a response

    :param str text: the text to be returned with the response
    """
    def __init__(self, text):
        self.headers = {"content-type": "text/xml"}
        self.status_code = 200
        self.text = text

def simulate_bgg_collection(params):
    supported_users = {
            TEST_VALID_USER: FAGENTU007_XML_FILENAME,
            TEST_INVALID_USER: INVALID_COLLECTION_XML_FILENAME
            }

    try:
        filename = supported_users[params["username"]]
    except KeyError as e:
        raise Exception("Unknown user " + str(params) + " given to simulate_bgg_collection")

    with open(filename, "r") as xmlfile:
        return xmlfile.read()

def simulate_bgg_search(params):
    supported_searches = {
            TEST_GAME_NAME: SEARCH_AGRICOLA_XML_FILENAME,
            "coup": SEARCH_COUP_XML_FILENAME,
            "eclipse": SEARCH_ECLIPSE_XML_FILENAME,
            TEST_INVALID_GAME_NAME: INVALID_REQUEST_XML_FILENAME
            }

    try:
        filename = supported_searches[params["query"]]
    except KeyError as e:
        raise Exception("Unknown query " + str(params) + " given to simulate_bgg_search")

    with open(filename, "r") as xmlfile:
        return xmlfile.read()

def simulate_bgg_thing(params):
    supported_things = {
            824: HIJARA_XML_FILENAME,
            1653: COUP_1653_XML_FILENAME,
            2088: COUP_2088_XML_FILENAME,
            8148: TRIO_XML_FILENAME,
            11542: ECLIPSE_11542_XML_FILENAME,
            23272: ECLIPSE_23272_XML_FILENAME,
            TEST_GAME_ID: AGRICOLA_XML_FILENAME,
            "31260,283": AGRICOLA_AND_ADVANCED_THIRD_REICH_XML_FILENAME,
            72125: ECLIPSE_72125_XML_FILENAME,
            TEST_GAME_ACCESSORY_ID: DESCENT_CONVERSION_KIT_XML_FILENAME,
            131357: COUP_131357_XML_FILENAME
            }

    try:
        filename = supported_things[params["id"]]
    except KeyError as e:
        raise Exception("Unknown ID " + str(params) + " given to simulate_bgg_thing")

    with open(filename, "r") as xmlfile:
        return xmlfile.read()

def simulate_bgg(url, params, timeout):
    supported_urls = {
            BGG_COLLECTION_URL: simulate_bgg_collection,
            BGG_SEARCH_URL: simulate_bgg_search,
            BGG_THING_URL: simulate_bgg_thing
            }

    try:
        simulator_function = supported_urls[url]
    except KeyError as e:
        raise Exception("Unknown url " + url + " given to simulate_bgg")

    response_text = simulator_function(params)
    return MockResponse(response_text)
