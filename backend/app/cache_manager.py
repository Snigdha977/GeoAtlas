from functools import lru_cache


@lru_cache(maxsize=100)
def cache_feed(feed_name):

    return feed_name
