from dataclasses import dataclass, field


@dataclass
class ScrapeConfig:
    sitemap_url: str
    output_file: str = "NotebookLM_Knowledge_Base.md"
    keywords: list[str] = field(
        default_factory=lambda: ["/blog/", "/docs/", "/whitepaper/", "/resources/"]
    )
    exclude_keywords: list[str] = field(
        default_factory=lambda: ["/careers/", "/contact/", "/privacy/", "/legal/"]
    )
    max_concurrent: int = 5
    rate_limit_delay: float = 1.0
    max_retries: int = 3
    cache_file: str = ".codescrap_cache.json"
    assets_dir: str = "assets"
    chunk_size: int = 480_000
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    )
    no_cache: bool = False
    clear_cache: bool = False
