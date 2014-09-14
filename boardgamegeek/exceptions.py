# boardgamegeek library base exception
class BoardGameGeekError(Exception):
    pass


class BoardGameGeekTimeoutError(BoardGameGeekError):
    pass


class BoardGameGeekAPIError(BoardGameGeekError):
    pass


class BoardGameGeekAPIRetryError(BoardGameGeekAPIError):
    pass


class BoardGameGeekAPINonXMLError(BoardGameGeekAPIError):
    pass
