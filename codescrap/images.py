import hashlib
import logging
from pathlib import Path
from urllib.parse import urlparse

from .networking import fetch_with_retry

logger = logging.getLogger(__name__)

MIN_IMAGE_SIZE = 1024  # skip images smaller than 1KB (tracking pixels)


def ensure_assets_dir(assets_dir: str) -> Path:
    path = Path(assets_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _image_filename(url: str) -> str:
    parsed = urlparse(url)
    ext = Path(parsed.path).suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"):
        ext = ".png"
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    return f"{url_hash}{ext}"


async def download_image(
    session, img_url: str, assets_dir: str, max_retries: int = 3
) -> str | None:
    try:
        data = await fetch_with_retry(session, img_url, max_retries)
        if len(data) < MIN_IMAGE_SIZE:
            return None

        assets_path = ensure_assets_dir(assets_dir)
        filename = _image_filename(img_url)
        filepath = assets_path / filename
        filepath.write_bytes(data)
        return f"{assets_dir}/{filename}"
    except Exception as e:
        logger.debug(f"Failed to download image {img_url}: {e}")
        return None
