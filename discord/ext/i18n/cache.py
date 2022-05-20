import json
import anyio
import asyncio

from os import path, curdir, mkdir
from .language import Language


class Cache:
    def __init__(self, dir="__lang_cache__", filename="cache.json") -> None:
        self.cache_dir = path.join(curdir, dir)
        self.cache_fn = filename
        self.cache_pth = path.join(self.cache_dir, self.cache_fn)
        self.sync_loaded = False

    async def load_cache(self):
        if not path.isfile(self.cache_pth):
            await self.empty()
        else:
            f = await anyio.open_file(self.cache_pth, mode="r", encoding="utf-8")
            self.internal_cache = json.loads(await f.read())
            await f.aclose()

    def load_cache_sync(self):
        """
        After the cache object is loaded in sync, it is incumbent on part of
        the cache users to keep it updated.
        """
        if not self.sync_loaded:
            self.sync_loaded = True
            if not path.isdir(self.cache_dir):
                self.internal_cache = {}
                if mkdir(self.cache_dir) == 1:
                    raise ValueError(
                        f"Could not make a cache folder at {self.cache_dir}"
                    )
                else:
                    open(self.cache_pth, mode=("w"), encoding="utf-8").close()
            else:
                with open(self.cache_pth, mode="r", encoding="utf-8") as f:
                    self.internal_cache = json.load(f)

    async def save_cache(self):
        f = await anyio.open_file(self.cache_pth, mode="w", encoding="utf-8")
        await f.write(json.dumps(self.internal_cache))
        await f.aclose()

    async def empty(self):
        """
        Empty the internal and external cache.
        """
        f = await anyio.open_file(self.cache_pth, mode="w", encoding="utf-8")
        await f.write("{}")
        await f.aclose()
        self.internal_cache = {}

    def task(self, coro):
        asyncio.create_task(coro)

    def set_cache(self, src: str, lang: Language, translated: str):
        if src in self.internal_cache:
            self.internal_cache[src][lang.code] = translated
        else:
            self.internal_cache[src] = {lang.code: translated}
        self.task(self.save_cache())

    def get_cache(self, src: str, lang: Language):
        if src in self.internal_cache and lang.code in self.internal_cache[src]:
            return self.internal_cache[src][lang.code]
