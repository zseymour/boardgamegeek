import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError as ETParseError
import requests_cache

try:
    import urllib.parse as urlparse
except:
    import urlparse

from .exceptions import BoardGameGeekAPIError, BoardGameGeekAPIRetryError, BoardGameGeekError


class DictObject(object):

    def __init__(self, data):
        self._data = data

    def __getattr__(self, item):
        # allow accessing user's variables using .attribute
        if item in self._data:
            return self._data[item]
        raise AttributeError

    def data(self):
        return self._data

    def __str__(self):
        return self.__unicode__().encode("utf-8")


def xml_subelement_attr(xml_elem, subelement, convert=None, attribute="value"):
    """
    Return the value of <xml_elem><subelement attribute="THIS" /></xml_elem>
    :param xml_elem: xml Element
    :param subelement: Name of the subelement to retrieve
    :param convert: if not None, a callable to perform the conversion of this attribute to a certain object type
    :param attribute: name of the attribute to get
    :return: value of the attribute
    """
    if xml_elem is None:
        return None

    subel = xml_elem.find(subelement)
    if subel is not None:
        value = subel.attrib.get(attribute)
        if convert and value is not None:
            value = convert(value)
        return value
    return None


def xml_subelement_attr_list(xml_elem, subelement, convert=None, attribute="value"):
    """
    Return the value of multiple subelements as a list
        <xml_elem>
            <subelement value="THIS" />
            <subelement value="THIS2" />
            ...
        </xml_elem>

    :param xml_elem: xml Element
    :param subelement: name of the subelement to retrieve
    :param convert: if not None, a callable used to perform the conversion of this attribute to a certain object type
    :param attribute: name of the attribute to get
    :return: list containing the values of the attributes
    """
    if xml_elem is None:
        return None

    subel = xml_elem.findall(subelement)
    res = []
    for e in subel:
        value = e.attrib.get(attribute)
        if convert and value is not None:
            value = convert(value)
        res.append(value)

    return res


def xml_subelement_text(xml_elem, subelement, convert=None):
    """
    Return the text from the specified subelement
    :param xml_elem: xml Element
    :param subelement: name of the subelement whose text will be retrieved
    :param convert: if not None, a callable used to perform the conversion of the text to a certain object type
    :return:
    """
    if xml_elem is None:
        return None

    subel = xml_elem.find(subelement)
    if subel is not None:
        text = subel.text
        if convert and text is not None:
            text = convert(text)
        return text
    return None


def get_parsed_xml_response(requests_session, url, params=None):
    """
    Returns a parsed XML

    :param url:
    :param params:
    :return:
    """
    try:
        r = requests_session.get(url, params=params)

        if r.status_code == 202:
            # BoardGameGeek API says that on status code 202 we need to retry the operation after a delay
            raise BoardGameGeekAPIRetryError()

        xml = r.text

        if sys.version_info >= (3,):
            root_elem = ET.fromstring(xml)
        else:
            utf8_xml = xml.encode("utf-8")
            root_elem = ET.fromstring(utf8_xml)

    except ETParseError as e:
        raise BoardGameGeekAPIError("error decoding BGG API response: {}".format(e))

    except Exception as e:
        raise BoardGameGeekAPIError("error fetching BGG API response: {}".format(e))

    return root_elem


def get_cache_session_from_uri(uri):
    """
    Returns a requests-cache session using caching specified in the URI. Valid uris are:

    * memory:///?ttl=<seconds>
    * sqlite:///path/to/sqlite.db?ttl=<seconds>&fast_save=<0|1>

    :param uri: URI specifying the type of cache to use and its parameters
    :return: CachedSession instance, which can be used as a regular ``requests`` session.
    :raises BoardGameGeekError in case of error
    """


    try:
        r = urlparse.urlparse(uri)

        args = urlparse.parse_qs(r.query)

        # if not specified, default cache time is 3600 seconds
        ttl = int(args.get("ttl", ['3600'])[0])

        if r.scheme == "memory":
            return requests_cache.core.CachedSession(backend="memory",
                                                     expire_after=ttl,
                                                     allowable_codes=(200,))

        elif r.scheme == "sqlite":
            fast_save = args.get("fast_save", ["0"])[0] != "0"
            return requests_cache.core.CachedSession(cache_name=r.path,
                                                     backend="sqlite",
                                                     expire_after=ttl,
                                                     extension="",
                                                     fast_save=fast_save,
                                                     allowable_codes=(200,))

        # TODO: add the redis backend
        # elif r.scheme == "redis":
        #     return requests_cache.core.CachedSession(cache_name=args.get("prefix", ["cache"])[0],
        #                                              backend="redis",
        #                                              expire_after=ttl,
        #                                              allowable_codes=(200,))

        # TODO: add the mongo backend

    except Exception as e:
        raise BoardGameGeekError("error trying to create a CachedSession from '{}': {}".format(uri, e))

    raise BoardGameGeekError("invalid cache URI: {}".format(uri))


