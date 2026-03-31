import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self, filepath: str):
        self._filepath = Path(filepath)
        self._data: dict[str, dict] = {}

    @classmethod
    def load(cls, filepath: str) -> "Cache":
        cache = cls(filepath)
        if cache._filepath.exists():
            try:
                cache._data = json.loads(cache._filepath.read_text())
                logger.info(f"Loaded cache with {len(cache._data)} entries")
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load cache, starting fresh: {e}")
                cache._data = {}
        return cache

    def has(self, url: str) -> bool:
        return url in self._data

    def add(self, url: str):
        self._data[url] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def save(self):
        self._filepath.write_text(json.dumps(self._data, indent=2))
        logger.info(f"Saved cache with {len(self._data)} entries")

    def clear(self):
        self._data = {}
        if self._filepath.exists():
            self._filepath.unlink()
            logger.info("Cache cleared")
