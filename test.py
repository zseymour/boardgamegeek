import sys
from boardgamegeek import BGGClient
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger()

bgg = BGGClient()
QUERY="Achtung Cthulhu"
games = bgg.search(QUERY, search_type=['rpgitem'])
bgg.game(game_id=games[0].id)._format(log)
        
