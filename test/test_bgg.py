# coding: utf-8

import pytest

from boardgamegeek import BoardGameGeek, BoardGameGeekError

progress_called = False


def progress_cb(items, total):
    global progress_called
    progress_called = True


def test_user_fetch():
    global progress_called

    #
    # Kinda hard to test without having a "test" user
    #
    bgg = BoardGameGeek()

    user = bgg.user("fagentu007", progress=progress_cb)

    assert user is not None
    assert user.name == "fagentu007"
    assert user.id == 818216
    assert progress_called

    assert type(user.buddies) == list
    assert type(user.guilds) == list

    progress_called = False

    # test with some user that doesn't exist
    with pytest.raises(BoardGameGeekError):
        bgg.user("someOneThatHopefullyWontExistPlsGuysDontCreateThisUser")


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

    assert game.alternative_names == [u"Bedrock",
                                      u"Enredos",
                                      u"The Jungle Book Twister",
                                      u"Let's Twist Again",
                                      u"Lil' Twister",
                                      u"Melktwister",
                                      u"Pretzel",
                                      u"Twist",
                                      u"Twister Kersteditie",
                                      u"Twister Pink",
                                      u"Wygibajtus",
                                      u"Твистер",
                                      u"פלונטר" ]

    # some not so exact assertions
    assert game.users_rated >= 1965
    assert 0.0 <= game.rating_average <= 10.0
    assert 0.0 <= game.rating_bayes_average <= 10.0
