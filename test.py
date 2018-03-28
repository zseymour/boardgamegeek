import sys
from boardgamegeek import BGGClient
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger()

bgg = BGGClient()
QUERY="Xanathar's"
games = bgg.search(QUERY, search_type=['rpgitem'])
for g in games[:25]:
    bgg.game(game_id=g.id)._format(log)
