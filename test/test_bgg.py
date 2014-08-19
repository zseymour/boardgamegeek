# coding: utf-8
from __future__ import unicode_literals

import os
import tempfile
import pytest

from boardgamegeek import BoardGameGeek, BoardGameGeekError

progress_called = False

TEST_VALID_USER = "fagentu007"
TEST_INVALID_USER = "someOneThatHopefullyWontExistPlsGuysDontCreateThisUser"
TEST_GUILD_ID = 669


def progress_cb(items, total):
    global progress_called
    progress_called = True


def test_caching():

    # test that we can disable caching
    bgg = BoardGameGeek(cache=None)

    user = bgg.user(TEST_VALID_USER)

    assert user is not None
    assert user.name == TEST_VALID_USER

    # test that we can use the SQLite cache
    # generate a temporary file
    fd, name = tempfile.mkstemp(suffix=".cache")

    # close the file and unlink it, we only need the temporary name
    os.close(fd)
    os.unlink(name)

    assert not os.path.isfile(name)

    with pytest.raises(BoardGameGeekError):
        # invalid value for the ttl parameter
        bgg = BoardGameGeek(cache="sqlite://{}?ttl=blabla&fast_save=0".format(name))

    bgg = BoardGameGeek(cache="sqlite://{}?ttl=1000".format(name))

    user = bgg.user(TEST_VALID_USER)
    assert user is not None
    assert user.name == TEST_VALID_USER

    assert os.path.isfile(name)

    # clean up..
    os.unlink(name)


def test_user_fetch():
    global progress_called

    #
    # Kinda hard to test without having a "test" user
    #
    bgg = BoardGameGeek()

    user = bgg.user(TEST_VALID_USER, progress=progress_cb)

    assert user is not None
    assert user.name == TEST_VALID_USER
    assert type(user.id) == int
    assert progress_called

    assert type(user.buddies) == list
    assert type(user.guilds) == list

    progress_called = False

    # test with some user that doesn't exist
    with pytest.raises(BoardGameGeekError):
        bgg.user(TEST_INVALID_USER)

    str(user)
    repr(user)


def test_collection_fetch():
    bgg = BoardGameGeek()

    with pytest.raises(BoardGameGeekError):
        bgg.collection(TEST_INVALID_USER)

    c = bgg.collection(TEST_VALID_USER)

    assert c is not None
    assert c.owner == TEST_VALID_USER
    assert type(len(c)) == int
    assert type(c.items) == list

    # make sure we can iterate through the collection
    for g in c:
        pass

    str(c)
    repr(c)


def test_guild_fetch():
    bgg = BoardGameGeek()

    guild = bgg.guild(TEST_GUILD_ID)

    assert guild.id == TEST_GUILD_ID
    assert guild.name == "BGG in Romana"

    for member in guild:
        pass

    str(guild)
    repr(guild)


def test_game_fetch():
    bgg = BoardGameGeek()

    # use an older game that's not so likely to change
    game = bgg.game("Twister")

    assert game is not None
    assert game.name == "Twister"
    assert game.id == 5894
    assert game.year == 1966
    assert game.mechanics == ["Player Elimination", "Roll / Spin and Move"]
    assert game.min_players == 2
    assert game.max_players == 4
    assert game.thumbnail == "http://cf.geekdo-images.com/images/pic196428_t.jpg"
    assert game.image == "http://cf.geekdo-images.com/images/pic196428.jpg"
    assert game.playing_time == 10
    assert game.min_age == 6
    assert game.categories == ["Action / Dexterity", "Children's Game", "Party Game"]
    assert game.families == ["Bratz", "Celebrities: Walt Disney", "Hello Kitty", "Promotional Board Games",
                             "TV Series: Sesame Street", "TV Series: Tweenies", "Twister"]
    assert game.designers == ["Chuck Foley", "Reyn Guyer", "Neil W. Rabens"]

    assert game.publishers == ["Altap", "Arrow Games Ltd", "Basic Fun, Inc.", "Game Office",
                               "Hasbro", "Jumbo", "Kidconnection", "Kids Fun Factory",
                               "MB Juegos", "MB Spellen", "MB Spiele", "Milton Bradley", "Tri-ang"]

    assert game.alternative_names == ["Bedrock",
                                      "Enredos",
                                      "The Jungle Book Twister",
                                      "Let's Twist Again",
                                      "Lil' Twister",
                                      "Melktwister",
                                      "Pretzel",
                                      "Twist",
                                      "Twister Kersteditie",
                                      "Twister Pink",
                                      "Wygibajtus",
                                      "Твистер",
                                      "פלונטר" ]

    # some not so exact assertions
    assert game.users_rated >= 1965
    assert 0.0 <= game.rating_average <= 10.0
    assert 0.0 <= game.rating_bayes_average <= 10.0

    # make sure no exception gets thrown
    str(game)
    repr(game)