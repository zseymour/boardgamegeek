import sys
from boardgamegeek import BGGClient
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()

bgg = BGGClient()
QUERY="Xanathar's"
games = bgg.search(QUERY, search_type=['rpgitem'])
for g in games[:25]:
    bg = bgg.game(game_id=g.id)
    log.info(bg.name)
    for s in bg.systems:
        log.info(s)
        log.info(bgg.family(name=s).description)
        
