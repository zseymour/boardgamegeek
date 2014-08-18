import argparse
import logging

from boardgamegeek.api import BoardGameGeek


def main():
    p = argparse.ArgumentParser(prog="boardgamegeek")

    p.add_argument("-u", "--user", help="Query by username")
    p.add_argument("-g", "--game", help="Query by game name")
    p.add_argument("-G", "--guild", help="Query by guild id")
    p.add_argument("-c", "--collection", help="Query user's collection")
    p.add_argument("--debug", action="store_true")

    args = p.parse_args()

    log = logging.getLogger("boardgamegeek")
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        # make requests shush
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.basicConfig(level=logging.INFO)

    def progress_cb(items, total):
        log.debug("fetching items: {}% complete".format(items*100/total))

    bgg = BoardGameGeek()

    if args.user:
        user = bgg.user(args.user, progress=progress_cb)
        if user:
            user._format(log)

    if args.game:
        game = bgg.game(args.game)
        if game:
            game._format(log)

    if args.guild:
        guild = bgg.guild(args.guild, progress=progress_cb)
        if guild:
            guild._format(log)

    if args.collection:
        collection = bgg.collection(args.collection)
        if collection:
            collection._format(log)

