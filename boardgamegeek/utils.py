
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