# coding: utf-8
from __future__ import unicode_literals

import logging
import os
import tempfile
import pytest
import xml.etree.ElementTree as ET
from boardgamegeek import BoardGameGeek, BoardGameGeekError
import boardgamegeek.utils as bggutil
import datetime

progress_called = False

# Kinda hard to test without having a "test" user
TEST_VALID_USER = "fagentu007"
TEST_VALID_USER_ID = 818216
TEST_USER_WITH_LOTS_OF_FRIENDS = "Solamar"        # user chosen randomly (..after a long search :)) ), just needed
                                                  # someone with lots of friends :D
TEST_INVALID_USER = "someOneThatHopefullyWontExistPlsGuysDontCreateThisUser"
TEST_INVALID_GAME_NAME = "blablablathisgamewonteverexist"
TEST_GAME_NAME = "Agricola"
TEST_GAME_ID = 31260

TEST_GAME_NAME_2 = "Inrah"
TEST_GAME_ID_2 = 86084  # a game with very few plays


TEST_GUILD_ID = 1229
TEST_GUILD_ID_2 = 930

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
    return BoardGameGeek()

@pytest.fixture
def null_logger():
    # create logger
    logger = logging.getLogger("null")
    logger.setLevel(logging.ERROR)
    return logger


def progress_cb(items, total):
    global progress_called
    progress_called = True


#
# Test caches
#
def test_no_caching():

    # test that we can disable caching
    bgg = BoardGameGeek(cache=None)

    user = bgg.user(TEST_VALID_USER)

    assert user is not None
    assert user.name == TEST_VALID_USER


def test_sqlite_caching():
    # test that we can use the SQLite cache
    # generate a temporary file
    fd, name = tempfile.mkstemp(suffix=".cache")

    # close the file and unlink it, we only need the temporary name
    os.close(fd)
    os.unlink(name)

    assert not os.path.isfile(name)

    with pytest.raises(BoardGameGeekError):
        # invalid value for the ttl parameter
        BoardGameGeek(cache="sqlite://{}?ttl=blabla&fast_save=0".format(name))

    bgg = BoardGameGeek(cache="sqlite://{}?ttl=1000".format(name))

    user = bgg.user(TEST_VALID_USER)
    assert user is not None
    assert user.name == TEST_VALID_USER

    assert os.path.isfile(name)

    # clean up..
    os.unlink(name)


#
# Users testing
#
def test_get_user_with_invalid_parameters(bgg):
    # test how the module reacts to unexpected parameters
    for invalid in [None, ""]:
        with pytest.raises(BoardGameGeekError):
            bgg.user(invalid)


def test_get_invalid_user_info(bgg):
    global progress_called

    progress_called = False
    user = bgg.user(TEST_INVALID_USER, progress=progress_cb)

    assert user is None
    assert not progress_called


def test_get_valid_user_info(bgg, null_logger):
    global progress_called

    progress_called = False
    user = bgg.user(TEST_USER_WITH_LOTS_OF_FRIENDS, progress=progress_cb)

    assert user is not None
    assert user.name == TEST_USER_WITH_LOTS_OF_FRIENDS
    assert type(user.id) == int
    assert progress_called

    assert type(user.buddies) == list
    assert type(user.guilds) == list

    str(user)
    repr(user)

    for buddy in user.buddies:
        str(buddy)
        repr(buddy)

    for guild in user.guilds:
        repr(guild)

    # for coverage's sake
    user._format(null_logger)
    assert type(user.data()) == dict


#
# Collections testing
#
def test_get_collection_with_invalid_parameters(bgg):
    for invalid in [None, ""]:
        with pytest.raises(BoardGameGeekError):
            bgg.collection(invalid)


def test_get_invalid_users_collection(bgg):

    collection = bgg.collection(TEST_INVALID_USER)
    assert collection is None


def test_get_valid_users_collection(bgg, null_logger):

    collection = bgg.collection(TEST_VALID_USER)

    assert collection is not None
    assert collection.owner == TEST_VALID_USER
    assert type(len(collection)) == int
    assert type(collection.items) == list

    # make sure we can iterate through the collection
    for g in collection:
        assert type(g.id) == int
        repr(g)

    str(collection)
    repr(collection)

    # for coverage's sake
    collection._format(null_logger)
    assert type(collection.data()) == dict


#
# Guild testing
#
def test_get_guild_with_invalid_parameters(bgg):
    # test how the module reacts to unexpected parameters
    for invalid in [None, [], {}]:
        with pytest.raises(BoardGameGeekError):
            bgg.guild(invalid)


def test_get_valid_guild_info(bgg, null_logger):
    global progress_called

    progress_called = False
    # Test with a guild with a big number members so that we can cover the code that fetches the next pages
    guild = bgg.guild(TEST_GUILD_ID, progress=progress_cb)

    assert progress_called
    assert guild.id == TEST_GUILD_ID
    assert guild.name == "Geek Tools"

    assert guild.addr1 is None
    assert guild.addr2 is None
    assert guild.address is None

    for member in guild:
        pass

    repr(guild)

    assert len(guild) > 0

    # for coverage's sake
    guild._format(null_logger)
    assert type(guild.data()) == dict

    # try to fetch a guild that also has an address besides members :D
    guild = bgg.guild(TEST_GUILD_ID_2)

    assert guild.id == TEST_GUILD_ID_2
    assert guild.addr1 is not None
    assert guild.addr2 is not None
    assert guild.address == "{} {}".format(guild.addr1, guild.addr2)


def test_get_invalid_guild_info(bgg):
    global progress_called

    progress_called = False
    guild = bgg.guild(0, progress=progress_cb)

    assert guild is None
    assert not progress_called


#
# Game testing
#
def test_get_unknown_game_info(bgg):
    game = bgg.game(TEST_INVALID_GAME_NAME)
    assert game is None


def test_get_game_with_invalid_parameters(bgg):
    with pytest.raises(BoardGameGeekError):
        bgg.game(name=None, game_id=None)

    for invalid in [None, ""]:
        with pytest.raises(BoardGameGeekError):
            bgg.game(invalid)

    for invalid in [None, "", "asd"]:
        with pytest.raises(BoardGameGeekError):
            bgg.game(None, game_id=invalid)


def check_game(game):
    assert game is not None
    assert game.name == TEST_GAME_NAME
    assert game.id == TEST_GAME_ID
    assert game.year == 2007
    assert game.mechanics == ["Area Enclosure", "Card Drafting", "Hand Management", "Worker Placement"]
    assert game.min_players == 1
    assert game.max_players == 5
    assert game.thumbnail == "http://cf.geekdo-images.com/images/pic259085_t.jpg"
    assert game.image == "http://cf.geekdo-images.com/images/pic259085.jpg"
    assert game.playing_time == 120
    assert game.min_age == 12
    assert game.categories == ["Economic", "Farming"]

    assert game.families == ["Agricola", "Animals: Cattle", "Animals: Sheep", "Harvest Series", "Solitaire Games"]

    assert game.designers == ["Uwe Rosenberg"]

    assert game.publishers == ["Lookout Games",
                               "999 Games",
                               "Brain Games",
                               "Compaya.hu - Gamer Café Kft.",
                               "Filosofia Édition",
                               "Hobby Japan",
                               "Hobby World",
                               "HomoLudicus",
                               "Korea Boardgames co., Ltd.",
                               "Lacerta",
                               "MINDOK",
                               "Smart Ltd",
                               "Stratelibri",
                               "Swan Panasia Co., Ltd.",
                               "Ystari Games",
                               "Z-Man Games"]

    assert game.alternative_names == ["Агрикола",
                                      "アグリコラ",
                                      "农场主",
                                      "農家樂",
                                      "아그리콜라"]

    # some not so exact assertions
    assert game.users_rated >= 34000
    assert 0.0 <= game.rating_average <= 10.0
    assert 0.0 <= game.rating_bayes_average <= 10.0

    assert type(game.rating_stddev) == float
    assert type(game.rating_median) == float
    assert game.rating_num_weights >= 0
    assert type(game.rating_average_weight) == float

    # make sure no exception gets thrown
    repr(game)


def test_get_known_game_info(bgg, null_logger):
    # use an older game that's not so likely to change
    game = bgg.game(TEST_GAME_NAME)

    check_game(game)

    # for coverage's sake
    game._format(null_logger)

    assert type(game.data()) == dict


def test_get_known_game_info_by_id(bgg):
    game = bgg.game(None, game_id=TEST_GAME_ID)
    check_game(game)


def test_get_game_id_by_name(bgg):
    game_id = bgg.get_game_id(TEST_GAME_NAME)
    assert game_id == TEST_GAME_ID


#
# Plays testing
#
def test_get_plays_with_invalid_parameters(bgg):
    with pytest.raises(BoardGameGeekError):
        bgg.plays(name=None, game_id=None)

    with pytest.raises(BoardGameGeekError):
        bgg.plays(name="", game_id=None)

    with pytest.raises(BoardGameGeekError):
        bgg.plays(name=None, game_id="asd")


def test_get_plays_with_unknown_username_and_id(bgg):
    plays = bgg.plays(name=TEST_INVALID_USER)
    assert plays is None

    # the api is a bit weird, if the game id is invalid, it still returns some answer, but of empty size
    plays = bgg.plays(name=None, game_id=1928391829)
    assert len(plays) == 0


def test_get_plays_of_user(bgg, null_logger):
    global progress_called

    plays = bgg.plays(name=TEST_VALID_USER, progress=progress_cb)

    assert plays.user == TEST_VALID_USER
    assert plays.user_id == TEST_VALID_USER_ID
    assert plays.game_id is None    # None since we got the plays for an user

    for p in plays.plays:
        assert type(p.id) == int
        assert p.user_id == TEST_VALID_USER_ID
        assert type(p.date) == datetime.datetime
        assert p.quantity >= 0
        assert p.duration >= 0
        assert type(p.incomplete) == int
        assert type(p.nowinstats) == int
        assert type(p.game_id) == int
        assert type(p.game_name) == str
        assert type(p.comment) in [type(None), str]

    plays._format(null_logger)


def test_get_plays_of_game(bgg, null_logger):
    global progress_called

    plays = bgg.plays(game_id=TEST_GAME_ID_2, progress=progress_cb)

    assert plays.user is None
    assert plays.user_id is None
    assert plays.game_id == TEST_GAME_ID_2

    for p in plays.plays:
        assert type(p.id) == int
        assert type(p.user_id) == int
        assert type(p.date) == datetime.datetime
        assert p.quantity >= 0
        assert p.duration >= 0
        assert type(p.incomplete) == int
        assert type(p.nowinstats) == int
        assert p.game_id == TEST_GAME_ID_2
        assert p.game_name == TEST_GAME_NAME_2
        assert type(p.comment) in [type(None), str]

    plays._format(null_logger)


#
# Utils testing
#
def test_get_xml_subelement_attr(xml):

    node = bggutil.xml_subelement_attr(None, "hello")
    assert node is None

    node = bggutil.xml_subelement_attr(xml, None)
    assert node is None

    node = bggutil.xml_subelement_attr(xml, "")
    assert node is None

    node = bggutil.xml_subelement_attr(xml, "node1", attribute="attr")
    assert node == "hello1"

    node = bggutil.xml_subelement_attr(xml, "node1", attribute="int_attr", convert=int)
    assert node == 1


def test_get_xml_subelement_attr_list(xml):

    node = bggutil.xml_subelement_attr_list(None, "list")
    assert node is None

    node = bggutil.xml_subelement_attr_list(xml, None)
    assert node is None

    node = bggutil.xml_subelement_attr_list(xml, "")
    assert node is None

    list_root = xml.find("list")
    node = bggutil.xml_subelement_attr_list(list_root, "li", attribute="attr")
    assert node == ["elem1", "elem2", "elem3", "elem4"]

    node = bggutil.xml_subelement_attr_list(list_root, "li", attribute="int_attr", convert=int)
    assert node == [1, 2, 3, 4]

    node = bggutil.xml_subelement_attr_list(xml, "node1", attribute="attr")
    assert node == ["hello1"]


def test_get_xml_subelement_text(xml):

    node = bggutil.xml_subelement_text(None, "node1")
    assert node is None

    node = bggutil.xml_subelement_text(xml, None)
    assert node is None

    node = bggutil.xml_subelement_text(None, "")
    assert node is None

    node = bggutil.xml_subelement_text(xml, "node1")
    assert node == "text"