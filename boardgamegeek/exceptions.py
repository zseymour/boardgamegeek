# boardgamegeek library base exception
class BoardGameGeekError(Exception):
    pass


class BoardGameGeekAPIRetryError(BoardGameGeekError):
    pass


class BoardGameGeekAPIError(BoardGameGeekError):
    pass

