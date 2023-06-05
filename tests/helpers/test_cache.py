import uuid

from pandasai.helpers.cache import Cache


class TestCache:
    def test_cache(self):
        cache_filename = f"cache_{uuid.uuid4().hex}"
        cache = Cache(filename=cache_filename)
        cache.set("key", "value")
        assert cache.get("key") == "value"

        cache.delete("key")
        print(cache.get("key"))
        assert cache.get("key") is None

        cache.destroy()
