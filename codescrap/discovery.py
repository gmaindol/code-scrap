import logging

from bs4 import BeautifulSoup

from .networking import fetch_with_retry

logger = logging.getLogger(__name__)


async def fetch_urls_from_sitemap(session, config, max_depth: int = 3) -> list[str]:
    urls = await _fetch_sitemap_recursive(
        session, config.sitemap_url, config.max_retries, max_depth
    )

    filtered = []
    for url in urls:
        url_lower = url.lower()
        if any(kw in url_lower for kw in config.exclude_keywords):
            continue
        if url_lower.endswith(".pdf") or any(
            kw in url_lower for kw in config.keywords
        ):
            filtered.append(url)

    unique = list(set(filtered))
    logger.info(f"Discovered {len(unique)} relevant URLs from sitemap")
    return unique


async def _fetch_sitemap_recursive(
    session, sitemap_url: str, max_retries: int, depth: int
) -> list[str]:
    if depth <= 0:
        return []

    logger.info(f"Fetching sitemap: {sitemap_url}")
    try:
        data = await fetch_with_retry(session, sitemap_url, max_retries)
        soup = BeautifulSoup(data, "lxml-xml")
    except Exception as e:
        logger.error(f"Failed to fetch sitemap {sitemap_url}: {e}")
        return []

    # Check for sitemap index
    sitemap_locs = soup.find_all("sitemap")
    if sitemap_locs:
        logger.info(
            f"Found sitemap index with {len(sitemap_locs)} child sitemaps"
        )
        urls = []
        for sitemap in sitemap_locs:
            loc = sitemap.find("loc")
            if loc:
                child_urls = await _fetch_sitemap_recursive(
                    session, loc.text.strip(), max_retries, depth - 1
                )
                urls.extend(child_urls)
        return urls

    # Regular sitemap — extract all <loc> URLs
    return [loc.text.strip() for loc in soup.find_all("loc")]
