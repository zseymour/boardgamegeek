from __future__ import unicode_literals

import argparse
import logging

from boardgamegeek.api import BoardGameGeek, HOT_ITEM_CHOICES


def brief_game_stats(game):
    num_owners = game.users_owned
    avg_rating = game.rating_average

    my_score = (num_owners / 100.0) * avg_rating

    log.info("Name        : {}".format(game.name))
    log.info("Categories  : {}".format(game.categories))
    log.info("Mechanics   : {}".format(game.mechanics))
    log.info("Players     : {}-{}".format(game.min_players, game.max_players))
    log.info("Age         : {}".format(game.min_age))
    log.info("Play time   : {}".format(game.playing_time))
    log.info("Game weight : {}".format(game.rating_average_weight))
    log.info("Score       : {}".format(game.rating_average))
    log.info("Votes       : {}".format(game.users_rated))
    log.info("MY SCORE    : {}".format(my_score))




def main():
    global log
    p = argparse.ArgumentParser(prog="boardgamegeek")

    p.add_argument("-u", "--user", help="Query by username")
    p.add_argument("-g", "--game", help="Query by game name")
    p.add_argument("--game-stats", help="Return brief statistics about the game")
    p.add_argument("-G", "--guild", help="Query by guild id")
    p.add_argument("-c", "--collection", help="Query user's collection")
    p.add_argument("-p", "--plays", help="Query user's play list")
    p.add_argument("-P", "--plays-by-game", help="Query a game's plays")
    p.add_argument("-H", "--hot-items", help="List all hot items by type", choices=HOT_ITEM_CHOICES)
    p.add_argument("-S", "--search", help="search and return results")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--retries", help="number of retries to perform in case of timeout or API HTTP 202 code",
                   type=int,
                   default=5)
    p.add_argument("--timeout", help="Timeout for API operations", type=int, default=10)

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

    bgg = BoardGameGeek(timeout=args.timeout, retries=args.retries)

    if args.user:
        user = bgg.user(args.user, progress=progress_cb)
        if user:
            user._format(log)

    if args.game:
        game = bgg.game(args.game)
        if game:
            game._format(log)

    if args.game_stats:
        game = bgg.game(args.game_stats)
        if game:
            brief_game_stats(game)

    if args.guild:
        guild = bgg.guild(args.guild, progress=progress_cb)
        if guild:
            guild._format(log)

    if args.collection:
        collection = bgg.collection(args.collection)
        if collection:
            collection._format(log)

    if args.plays:
        plays = bgg.plays(name=args.plays, progress=progress_cb)
        if plays:
            plays._format(log)

    if args.plays_by_game:
        try:
            game_id = int(args.plays_by_game)
        except:
            game_id = bgg.get_game_id(args.plays_by_game)

        plays = bgg.plays(game_id=game_id, progress=progress_cb)
        if plays:
            plays._format(log)

    if args.hot_items:
        hot_items = bgg.hot_items(args.hot_items)
        for item in hot_items:
            item._format(log)

    if args.search:
        # TODO: add search type..
        results = bgg.search(args.search)
        if results:
            for r in results:
                r._format(log)

if __name__ == "__main__":
    main()