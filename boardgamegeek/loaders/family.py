import logging
import re
from dateutil import parser as datetime_parser

from ..objects.families import Family
from ..exceptions import BGGApiError
from ..utils import xml_subelement_attr_list, xml_subelement_text, xml_subelement_attr, get_board_game_version_from_element


log = logging.getLogger("boardgamegeek.loaders.game")

def create_family_from_xml(xml_root, family_id, html_parser):
    family_type = xml_root.attrib["type"]
    data = {"id": family_id,
            "type": family_type,
            "name": xml_subelement_attr(xml_root, "name[@type='primary']"),
            "alternative_names": xml_subelement_attr_list(xml_root, "name[@type='alternate']"),
            "image": xml_subelement_text(xml_root, "image"),
            "thumbnail": xml_subelement_text(xml_root, "thumbnail"),
            "family_members": xml_subelement_attr_list(xml_root, "link[@type='{}']".format(family_type)),
            "description": xml_subelement_text(xml_root, "description", convert=html_parser.unescape, quiet=True)}

    # Look for the videos
    # TODO: The BGG API doesn't take the page=NNN parameter into account for videos; when it does, paginate them too
    videos = xml_root.find("videos")
    if videos is not None:
        vid_list = []
        for vid in videos.findall("video"):
            try:
                vd = {"id": vid.attrib["id"],
                      "name": vid.attrib["title"],
                      "category": vid.attrib.get("category"),
                      "language": vid.attrib.get("language"),
                      "link": vid.attrib["link"],
                      "uploader": vid.attrib.get("username"),
                      "uploader_id": vid.attrib.get("userid"),
                      "post_date": vid.attrib.get("postdate")
                      }
                vid_list.append(vd)
            except KeyError:
                raise BGGApiError("malformed XML element ('video')")

        data["videos"] = vid_list

    # look for the versions
    versions = xml_root.find("versions")
    if versions is not None:
        ver_list = []

        for version in versions.findall("item[@type='boardgameversion']"):
            try:
                vd = get_board_game_version_from_element(version)
                ver_list.append(vd)
            except KeyError:
                raise BGGApiError("malformed XML element ('versions')")

        data["versions"] = ver_list

    # look for the statistics
    stats = xml_root.find("statistics/ratings")
    if stats is not None:
        sd = {
            "usersrated": xml_subelement_attr(stats, "usersrated", convert=int, quiet=True),
            "average": xml_subelement_attr(stats, "average", convert=float, quiet=True),
            "bayesaverage": xml_subelement_attr(stats, "bayesaverage", convert=float, quiet=True),
            "stddev": xml_subelement_attr(stats, "stddev", convert=float, quiet=True),
            "median": xml_subelement_attr(stats, "median", convert=float, quiet=True),
            "owned": xml_subelement_attr(stats, "owned", convert=int, quiet=True),
            "trading": xml_subelement_attr(stats, "trading", convert=int, quiet=True),
            "wanting": xml_subelement_attr(stats, "wanting", convert=int, quiet=True),
            "wishing": xml_subelement_attr(stats, "wishing", convert=int, quiet=True),
            "numcomments": xml_subelement_attr(stats, "numcomments", convert=int, quiet=True),
            "numweights": xml_subelement_attr(stats, "numweights", convert=int, quiet=True),
            "averageweight": xml_subelement_attr(stats, "averageweight", convert=float, quiet=True),
            "ranks": []
        }

        ranks = stats.findall("ranks/rank")
        for rank in ranks:
            try:
                rank_value = int(rank.attrib.get("value"))
            except:
                rank_value = None
            sd["ranks"].append({"id": rank.attrib["id"],
                                "name": rank.attrib["name"],
                                "friendlyname": rank.attrib.get("friendlyname"),
                                "value": rank_value})

        data["stats"] = sd

        polls = xml_root.findall("poll")
        data["suggested_players"] = {}
        for poll in polls:
            if poll.attrib.get("name") == "suggested_numplayers":
                results = poll.findall('results')
                data["suggested_players"]['total_votes'] = poll.attrib.get('totalvotes')
                data["suggested_players"]['results'] = {}
                for result in results:
                    player_count = result.attrib.get("numplayers")
                    if result.find("result[@value='Best']") is not None:
                        data["suggested_players"]['results'][player_count] = {
                            'best_rating': result.find("result[@value='Best']")
                            .attrib.get("numvotes"),
                            'recommended_rating': result
                            .find("result[@value='Recommended']").attrib.get("numvotes"),
                            'not_recommeded_rating': result
                            .find("result[@value='Not Recommended']")
                            .attrib.get("numvotes"),
                        }
                    else:
                        ''' if there is only one poll player count and no votes recorded
                            by default it is the the best player count '''
                        data["suggested_players"]['results'][player_count] = {
                            'best_rating': '1',
                            'recommended_rating': '0',
                            'not_recommeded_rating': '0',
                        }

    return Family(data)
