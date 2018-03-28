import sys
from boardgamegeek import BGGClient
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()

bgg = BGGClient()
QUERY="Dragon 1989"
games = bgg.search(QUERY, search_type=['rpgissue'])
for g in games[:25]:
    log.info(g.name)
