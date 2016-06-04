import requests
import requests_cache


class CacheBackend(object):
    pass


class CacheBackendNone(CacheBackend):
    def __init__(self):
        self.cache = requests.Session()


class CacheBackendMemory(CacheBackend):
    """ Cache HTTP requests in memory """
    def __init__(self, ttl):
        self.cache = requests_cache.core.CachedSession(backend="memory", expire_after=ttl, allowable_codes=(200,))


class CacheBackendSqlite(CacheBackend):
    def __init__(self, path, ttl, fast_save=True):
        self.cache = requests_cache.core.CachedSession(cache_name=path,
                                                       backend="sqlite",
                                                       expire_after=ttl,
                                                       extension="",
                                                       fast_save=fast_save,
                                                       allowable_codes=(200,))
