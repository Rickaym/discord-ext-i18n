import json
import anyio
import zlib

from os import path, curdir, mkdir
from sys import getsizeof

from typing import Union


class Cache:
    def __init__(self, dir="./__lang_cache__/", filename="cache.json") -> None:
        self.cache_dir = path.join(curdir, dir)
        self.cache_fn = filename
        self.cache_pth = path.join(self.cache_dir, self.cache_fn)
        if not path.isdir(self.cache_dir):
            if mkdir(dir) == 1:
                raise ValueError(f"Could not make a cache folder at {self.cache_dir}")

    async def load_cache(self):
        if not path.isfile(self.cache_pth):
            await self.empty()
        else:
            f = await anyio.open_file(
                path.join(self.cache_dir, self.cache_fn), mode="r", encoding="utf-8"
            )
            self.internal_cache = json.loads(await f.read())
            await f.aclose()

    async def empty(self):
        """
        Empty the internal and external cache.
        """
        f = await anyio.open_file(self.cache_dir, mode="w", encoding="utf-8")
        await f.write("{}")
        await f.aclose()
        self.internal_cache = {}

    @staticmethod
    def shallow_compress(src: Union[str, bytes]):
        """
        Compresses if lossless compression makes source string
        smaller, if not returns the original string.
        """
        if isinstance(src, str):
            src = src.encode()
        comp_src = zlib.compress(src)
        if getsizeof(src) >= getsizeof(comp_src):
            comp_src = src
        return comp_src.decode()

    @staticmethod
    def shallow_decompress(compressed: Union[str, bytes]):
        """
        Compresses if lossless compression makes source string
        smaller, if not returns the original string.
        """
        if isinstance(compressed, str):
            compressed = compressed.encode()
        try:
            src = zlib.decompress(compressed)
        except zlib.error:
            src = compressed
        return src.decode()

    def get_cache(self, lang: str, src: Union[str, bytes]):
        if isinstance(src, str):
            src = src.encode()
        comp_src = self.shallow_compress(src)
        if comp_src in self.internal_cache:
            return zlib.decompress(self.internal_cache[comp_src][lang]).decode()
