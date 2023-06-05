from pandasai.helpers.cache import Cache


class TestCache:
    def test_cache(self):
        cache = Cache()
        cache.set("key", "value")
        assert cache.get("key") == "value"

        cache.delete("key")
        print(cache.get("key"))
        assert cache.get("key") is None
