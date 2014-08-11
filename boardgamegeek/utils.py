import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError as ETParseError


from .exceptions import BoardGameGeekAPIError


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
        xml = requests_session.get(url, params=params).text

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
