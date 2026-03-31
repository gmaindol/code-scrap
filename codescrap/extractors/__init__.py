from .html import extract_html
from .pdf import extract_pdf
from .openapi import extract_openapi


async def extract(url: str, session, browser, config) -> str:
    url_lower = url.lower()

    if url_lower.endswith(".pdf"):
        return await extract_pdf(session, url, config)
    elif (
        url_lower.endswith((".json", ".yaml", ".yml"))
        or "openapi" in url_lower
        or "swagger" in url_lower
    ):
        return await extract_openapi(session, url, config)
    else:
        return await extract_html(session, url, browser, config)
