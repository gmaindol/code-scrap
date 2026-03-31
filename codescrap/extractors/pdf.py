import asyncio
import io
import logging

import pdfplumber

from ..images import ensure_assets_dir
from ..networking import fetch_with_retry

logger = logging.getLogger(__name__)


async def extract_pdf(session, pdf_url: str, config) -> str:
    try:
        data = await fetch_with_retry(session, pdf_url, config.max_retries)
        text, image_paths = await asyncio.to_thread(
            _process_pdf, data, pdf_url, config.assets_dir
        )

        result = f"## Source URL: {pdf_url} (PDF Document)\n\n{text}"
        if image_paths:
            result += "\n\n### Images\n"
            result += "\n".join(f"![PDF image]({p})" for p in image_paths)
        result += "\n\n---\n\n"
        return result

    except Exception as e:
        logger.error(f"Failed to extract PDF {pdf_url}: {e}")
        return f"## Source URL: {pdf_url}\n*Failed to extract PDF: {e}*\n\n---\n\n"


def _process_pdf(data: bytes, pdf_url: str, assets_dir: str) -> tuple[str, list[str]]:
    import hashlib
    from pathlib import Path

    text_parts = []
    image_paths = []

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

            # Extract embedded images
            if hasattr(page, "images") and page.images:
                assets_path = ensure_assets_dir(assets_dir)
                for img_idx, img in enumerate(page.images):
                    try:
                        img_obj = page.crop(
                            (img["x0"], img["top"], img["x1"], img["bottom"])
                        ).to_image(resolution=150)
                        url_hash = hashlib.sha256(pdf_url.encode()).hexdigest()[:12]
                        filename = f"pdf_{url_hash}_p{page_num}_i{img_idx}.png"
                        filepath = assets_path / filename
                        img_obj.save(str(filepath))
                        image_paths.append(f"{assets_dir}/{filename}")
                    except Exception as e:
                        logger.debug(
                            f"Failed to extract image from page {page_num}: {e}"
                        )

    return "\n".join(text_parts), image_paths
