from _common import *
from boardgamegeek import BGGError


def test_search(bgg):
    res = bgg.search("some invalid game name", exact=True)
    assert not len(res)

    res = bgg.search("Twilight Struggle", exact=True)
    assert len(res)

    # test that the new type of search works
    res = bgg.search("Agricola", search_type=["boardgame"])
    assert type(res[0].id) == int

    with pytest.raises(BGGError):
        bgg.search("Agricola", search_type=["invalid-search-type"])