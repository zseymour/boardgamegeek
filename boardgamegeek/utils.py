# coding: utf-8
"""
:mod:`boardgamegeek.utils` - Generic helper functions
=====================================================

.. module:: boardgamegeek.utils
   :platform: Unix, Windows
   :synopsis: generic helper functions

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>

"""
from __future__ import unicode_literals
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError as ETParseError
import requests_cache
import requests

try:
    import urllib.parse as urlparse
except:
    import urlparse

from .exceptions import BoardGameGeekAPIError, BoardGameGeekAPIRetryError, BoardGameGeekError, BoardGameGeekAPINonXMLError


class DictObject(object):
    """
    Just a fancy wrapper over a dictionary
    """

    def __init__(self, data):
        self._data = data

    def __getattr__(self, item):
        # allow accessing user's variables using .attribute
        if item in self._data:
            return self._data[item]
        raise AttributeError

    def data(self):
        """
        Access to the internal data dictionary, for easy dumping
        :return: the internal data dictionary
        """
        return self._data


def xml_subelement_attr(xml_elem, subelement, convert=None, attribute="value"):
    """
    Search for a sub-element and return the value of its attribute.

    For the following XML document:

    .. code-block:: xml

        <xml_elem>
            <subelement value="THIS" />
        </xml_elem>

    a call to ``xml_subelement_attr(xml_elem, "subelement")`` would return ``"THIS"``


    :param xml_elem: search the children nodes of this element
    :param subelement: Name of the sub-element to search for
    :param convert: if not None, a callable to perform the conversion of this attribute to a certain object type
    :param attribute: name of the attribute to get
    :return: value of the attribute or ``None`` in error cases

    """
    if xml_elem is None or not subelement:
        return None

    value = None
    subel = xml_elem.find(subelement)
    if subel is not None:
        value = subel.attrib.get(attribute)
        if convert and value is not None:
            value = convert(value)
    return value


def xml_subelement_attr_list(xml_elem, subelement, convert=None, attribute="value"):
    """
    Search for sub-elements and return a list of the specified attribute.

    .. code-block:: xml

        <xml_elem>
            <subelement value="THIS" />
            <subelement value="THIS2" />
            ...
        </xml_elem>

    For the above document, ["THIS", "THIS2"] will be returned

    :param xml_elem: search the children nodes of this element
    :param subelement: name of the sub-element to search for
    :param convert: if not None, a callable used to perform the conversion of this attribute to a certain object type
    :param attribute: name of the attribute to get
    :return: list containing the values of the attributes or ``None`` in error cases
    """
    if xml_elem is None or not subelement:
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
    Return the text of the specified subelement

    For the document below:

    .. code-block:: xml

        <xml_elem>
            <subelement>text</subelement>
        </xml_elem>

    ``"text"`` will be returned

    :param xml_elem: search the children nodes of this element
    :param subelement: name of the subelement whose text will be retrieved
    :param convert: if not None, a callable used to perform the conversion of the text to a certain object type
    :return: The text associated with the sub-element or ``None`` in case of error
    """
    if xml_elem is None or not subelement:
        return None

    text = None
    subel = xml_elem.find(subelement)
    if subel is not None:
        text = subel.text
        if convert and text is not None:
            text = convert(text)
    return text


def get_parsed_xml_response(requests_session, url, params=None, timeout=5):
    """
    Downloads an XML from the specified url, parses it and returns the xml ElementTree.

    :param requests_session: A Session of the ``requests`` library, used to fetch the url
    :param url: the address where to get the XML from
    :param params: dictionary containing the parameters which should be sent with the request
    :return: :func:`xml.etree.ElementTree` corresponding to the XML
    :raises: :class:`BoardGameGeekAPIRetryError` if this request should be retried after a short delay
    :raises: :class:`BoardGameGeekAPIError` if the response couldn't be parsed
    """
    try:
        r = requests_session.get(url, params=params, timeout=timeout)

        if r.status_code == 202:
            # BoardGameGeek API says that on status code 202 we need to retry the operation after a delay
            raise BoardGameGeekAPIRetryError()

        if not r.headers.get("content-type").startswith("text/xml"):
            raise BoardGameGeekAPINonXMLError("non-XML reply")

        xml = r.text

        if sys.version_info >= (3,):
            root_elem = ET.fromstring(xml)
        else:
            utf8_xml = xml.encode("utf-8")
            root_elem = ET.fromstring(utf8_xml)

    except requests.exceptions.Timeout:
        raise BoardGameGeekError("API request timeout")

    except ETParseError as e:
        raise BoardGameGeekAPIError("error decoding BGG API response: {}".format(e))

    except (BoardGameGeekAPIRetryError, BoardGameGeekAPINonXMLError):
        raise

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
    :raises: :class:`BoardGameGeekError` in case of error
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


