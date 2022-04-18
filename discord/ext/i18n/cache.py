import json

class Cache:
    @staticmethod
    def empty_trans_cache():
        with open("bot/assets/trans_cache.json", "w") as f:
            json.dump({}, f)

    @staticmethod
    def cache_trans(lang: str, src: str, dest: str):
        with open("bot/assets/trans_cache.json", "r") as f:
            cache = json.load(f)
        try:
            lang_cache = cache[lang]
        except KeyError:
            cache[lang] = {src: dest}
        else:
            lang_cache[src] = dest
        with open("bot/assets/trans_cache.json", "w") as f:
            json.dump(cache, f, indent=4)

    @staticmethod
    def get_cache(lang: str, src: str):
        with open("bot/assets/trans_cache.json", "r") as f:
            cache = json.load(f)
        try:
            return cache[lang][src]
        except KeyError:
            return
