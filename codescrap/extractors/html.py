import asyncio
import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..images import download_image

logger = logging.getLogger(__name__)


async def extract_html(session, url: str, browser, config) -> str:
    try:
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            html_content = await page.content()
        finally:
            await page.close()

        return await _html_to_markdown(session, html_content, url, config)
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return f"## Source URL: {url}\n*Failed to extract content: {e}*\n\n---\n\n"


async def _html_to_markdown(session, html: str, url: str, config) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["nav", "footer", "script", "style", "header", "aside"]):
        element.decompose()

    main_content = soup.find("main") or soup.find("article") or soup.body
    if not main_content:
        return ""

    # Convert tables to Markdown before extracting text
    for table in main_content.find_all("table"):
        md_table = _table_to_markdown(table)
        table.replace_with(BeautifulSoup(f"\n{md_table}\n", "html.parser"))

    # Extract and download images
    image_refs = await _extract_images(session, main_content, url, config)

    text = main_content.get_text(separator="\n", strip=True)

    # Append image references at the end of the section
    if image_refs:
        text += "\n\n### Images\n" + "\n".join(image_refs)

    return f"## Source URL: {url} (HTML Webpage)\n\n{text}\n\n---\n\n"


def _table_to_markdown(table) -> str:
    rows = table.find_all("tr")
    if not rows:
        return ""

    md_rows = []
    for row in rows:
        cells = row.find_all(["th", "td"])
        cell_texts = [cell.get_text(strip=True).replace("|", "\\|") for cell in cells]
        md_rows.append("| " + " | ".join(cell_texts) + " |")

    if len(md_rows) < 1:
        return ""

    # Insert separator after first row (header)
    num_cols = md_rows[0].count("|") - 1
    separator = "| " + " | ".join(["---"] * num_cols) + " |"
    md_rows.insert(1, separator)

    return "\n".join(md_rows)


async def _extract_images(session, content, base_url: str, config) -> list[str]:
    refs = []
    tasks = []

    for img in content.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        # Resolve relative URLs
        img_url = urljoin(base_url, src)
        if not img_url.startswith(("http://", "https://")):
            continue
        # Skip CDN placeholders/assets (common on marketing sites, often blocked)
        if "cdn.prod.website-files.com" in img_url or "placeholder" in img_url.lower():
            continue
        alt = img.get("alt", "image")
        tasks.append((img_url, alt))

    # Download images concurrently
    results = await asyncio.gather(
        *[download_image(session, url, config.assets_dir, config.max_retries)
          for url, _ in tasks],
        return_exceptions=True,
    )

    for (img_url, alt), result in zip(tasks, results):
        if isinstance(result, str):
            refs.append(f"![{alt}]({result})")

    return refs
