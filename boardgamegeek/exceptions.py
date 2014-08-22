# boardgamegeek library base exception
class BoardGameGeekError(Exception):
    pass


class BoardGameGeekAPIError(BoardGameGeekError):
    pass


class BoardGameGeekAPIRetryError(BoardGameGeekAPIError):
    pass


class BoardGameGeekAPINonXMLError(BoardGameGeekAPIError):
    pass
