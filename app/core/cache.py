import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _CacheItem:
    expires_at: float
    value: Any


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, _CacheItem] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        if time.time() >= item.expires_at:
            self._store.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = _CacheItem(expires_at=time.time() + ttl_seconds, value=value)