import logging


from ..plays import UserPlays, GamePlays
from ..utils import xml_subelement_text, xml_subelement_attr


log = logging.getLogger("boardgamegeek.loaders.plays")


def create_plays_from_xml(xml_root, game_id=None):

    try:
        # in case of error, the root node doesn't have a 'total' attribute
        count = int(xml_root.attrib["total"])   # how many plays
    except:
        return None

    if game_id is None:
        # User's plays
        return UserPlays({"username": xml_root.attrib["username"],
                          "user_id": int(xml_root.attrib["userid"]),
                          "plays_count": count})
    else:
        return GamePlays({"game_id": game_id, "plays_count": count})


def add_plays_from_xml(plays, xml_root):

    added_plays = False

    for play in xml_root.findall("play"):

        added_plays = True

        player_list = []
        for player in play.findall("players/player"):
            player_data = {"username": player.attrib.get("username"),
                           "user_id": int(player.attrib.get("userid", -1)),
                           "name": player.attrib.get("name"),
                           "startposition": player.attrib.get("startposition"),
                           "new": player.attrib.get("new"),
                           "win": player.attrib.get("win"),
                           "rating": player.attrib.get("rating"),
                           "score": player.attrib.get("score")}

            player_list.append(player_data)

        # TODO: add the game subtype too
        data = {"id": int(play.attrib["id"]),
                "date": play.attrib["date"],
                "quantity": int(play.attrib["quantity"]),
                "duration": int(play.attrib["length"]),
                "incomplete": int(play.attrib["incomplete"]),
                "nowinstats": int(play.attrib["nowinstats"]),
                # for User plays, will be overwritten with the user id when adding the play.
                "user_id": int(play.attrib.get("userid", -1)),
                "game_id": xml_subelement_attr(play, "item", attribute="objectid", convert=int),
                "game_name": xml_subelement_attr(play, "item", attribute="name"),
                "comment": xml_subelement_text(play, "comments"),
                "players": player_list}

        plays.add_play(data)

    return added_plays
