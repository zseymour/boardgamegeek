import os
import tempfile

from _common import *
from boardgamegeek import BGGError


#
# Test caches
#
def test_no_caching():
    # test that we can disable caching
    bgg = BGGClient(cache=None)

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

    with pytest.raises(BGGError):
        # invalid value for the ttl parameter
        BGGClient(cache="sqlite://{}?ttl=blabla&fast_save=0".format(name))

    with pytest.raises(BGGError):
        BGGClient(cache="invalid://cache")

    bgg = BGGClient(cache="sqlite://{}?ttl=1000".format(name))

    user = bgg.user(TEST_VALID_USER)
    assert user is not None
    assert user.name == TEST_VALID_USER

    assert os.path.isfile(name)

    # clean up..
    os.unlink(name)

