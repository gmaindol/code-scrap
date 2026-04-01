import argparse
import asyncio
import logging
import sys
import aiohttp
from playwright.async_api import async_playwright

from .cache import Cache
from .config import ScrapeConfig
from .discovery import fetch_urls_from_sitemap
from .extractors import extract
from .networking import RateLimiter, create_session
from .output import compile_output

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> ScrapeConfig:
    parser = argparse.ArgumentParser(
        description="Scrape vendor websites into Markdown for NotebookLM"
    )
    parser.add_argument(
        "--sitemap-url", required=True, help="URL of the sitemap.xml to scrape"
    )
    parser.add_argument(
        "--output", default="NotebookLM_Knowledge_Base.md", help="Output filename"
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=None,
        help="URL path keywords to include (e.g. /docs/ /blog/)",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=None,
        help="URL path keywords to exclude (e.g. /careers/ /contact/)",
    )
    parser.add_argument(
        "--concurrency", type=int, default=5, help="Max concurrent requests"
    )
    parser.add_argument(
        "--rate-limit", type=float, default=1.0, help="Delay between requests (seconds)"
    )
    parser.add_argument(
        "--max-retries", type=int, default=3, help="Max retries per request"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=480_000,
        help="Max chars per output file (default 480000)",
    )
    parser.add_argument(
        "--assets-dir", default="assets", help="Directory for downloaded images"
    )
    parser.add_argument(
        "--user-agent", default=None, help="Custom User-Agent string (for bot detection bypass)"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Ignore existing cache"
    )
    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear cache before starting"
    )

    args = parser.parse_args(argv)

    config = ScrapeConfig(sitemap_url=args.sitemap_url)
    config.output_file = args.output
    config.max_concurrent = args.concurrency
    config.rate_limit_delay = args.rate_limit
    config.max_retries = args.max_retries
    config.chunk_size = args.chunk_size
    config.assets_dir = args.assets_dir
    config.no_cache = args.no_cache
    config.clear_cache = args.clear_cache
    if args.keywords:
        config.keywords = args.keywords
    if args.exclude:
        config.exclude_keywords = args.exclude
    if args.user_agent:
        config.user_agent = args.user_agent

    return config


async def run(config: ScrapeConfig):
    # Cache setup
    cache = Cache.load(config.cache_file)
    if config.clear_cache:
        cache.clear()

    # Discover URLs
    async with create_session(config) as session:
        urls = await fetch_urls_from_sitemap(session, config)

    if not urls:
        logger.error("No URLs found. Check your sitemap URL and keywords.")
        return

    # Filter cached URLs
    if not config.no_cache:
        before = len(urls)
        urls = [u for u in urls if not cache.has(u)]
        skipped = before - len(urls)
        if skipped:
            logger.info(f"Skipping {skipped} cached URLs, {len(urls)} remaining")

    if not urls:
        logger.info("All URLs already cached. Nothing to do.")
        return

    logger.info(f"Processing {len(urls)} URLs...")

    rate_limiter = RateLimiter(config.max_concurrent, config.rate_limit_delay)
    chunks = []
    failed = 0

    async with create_session(config) as session:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)

            async def process(url: str) -> str | None:
                async with rate_limiter:
                    try:
                        result = await extract(url, session, browser, config)
                        cache.add(url)
                        logger.info(f"OK: {url}")
                        return result
                    except Exception as e:
                        logger.error(f"FAIL: {url} - {e}")
                        return None

            results = await asyncio.gather(
                *[process(u) for u in urls], return_exceptions=True
            )
            await browser.close()

    for r in results:
        if isinstance(r, str) and r:
            chunks.append(r)
        else:
            failed += 1

    # Compile output
    written = compile_output(chunks, config)
    cache.save()

    # Summary
    logger.info(
        f"\nDone! Processed {len(chunks)} URLs, {failed} failed. "
        f"Output: {', '.join(written)}"
    )


def main(argv: list[str] | None = None):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    config = parse_args(argv)
    asyncio.run(run(config))


if __name__ == "__main__":
    main()
