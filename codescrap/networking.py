import asyncio
import random
import logging

import aiohttp

logger = logging.getLogger(__name__)


def create_session(config) -> aiohttp.ClientSession:
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {"User-Agent": config.user_agent}
    return aiohttp.ClientSession(timeout=timeout, headers=headers)


async def fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> bytes:
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            last_error = e
            if attempt < max_retries:
                delay = base_delay * (2**attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Retry {attempt + 1}/{max_retries} for {url} "
                    f"(waiting {delay:.1f}s): {e}"
                )
                await asyncio.sleep(delay)
    raise last_error


class RateLimiter:
    def __init__(self, max_concurrent: int, delay: float):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._delay = delay
        self._lock = asyncio.Lock()

    async def acquire(self):
        await self._semaphore.acquire()
        async with self._lock:
            await asyncio.sleep(self._delay)

    def release(self):
        self._semaphore.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        self.release()
