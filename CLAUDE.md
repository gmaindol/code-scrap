# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Async web scraping pipeline that discovers URLs from sitemaps (including sitemap indexes), extracts content and images from HTML pages, PDFs, and OpenAPI specs, then compiles everything into chunked Markdown files for NotebookLM.

## Setup

- Python 3.13 (see `.python-version`)
- Install deps: `pip install -r requirements.txt` or `pip install -e .`
- Playwright browser: `playwright install chromium`

## Running

```bash
# Basic usage
python main.py --sitemap-url https://example.com/sitemap.xml

# With options
python main.py --sitemap-url https://example.com/sitemap.xml \
  --output output.md \
  --keywords /docs/ /blog/ /api/ \
  --concurrency 3 \
  --rate-limit 2.0 \
  --no-cache

# Or via installed entry point
codescrap --sitemap-url https://example.com/sitemap.xml
```

Key CLI flags: `--concurrency`, `--rate-limit`, `--chunk-size`, `--no-cache`, `--clear-cache`, `--assets-dir`, `--exclude`

## Architecture

```
codescrap/
  cli.py          — argparse CLI + async orchestrator (run function)
  config.py       — ScrapeConfig dataclass with all settings
  discovery.py    — Async sitemap fetching with sitemap index recursion
  networking.py   — aiohttp session factory, fetch_with_retry (exp backoff), RateLimiter
  cache.py        — JSON-based URL cache for resumable runs
  images.py       — Image download helper (SHA256-hashed filenames → assets/)
  output.py       — Markdown compilation + chunking at 480K char boundaries
  extractors/
    __init__.py   — Router: dispatches URL to html/pdf/openapi extractor
    html.py       — Playwright async, HTML table→Markdown, image extraction
    pdf.py        — pdfplumber via asyncio.to_thread, embedded image extraction
    openapi.py    — JSON/YAML OpenAPI spec → structured Markdown
```

**Data flow**: CLI parses args → discover URLs from sitemap → filter by cache → extract concurrently (semaphore-bounded) → compile chunks → write output files + save cache

**Concurrency model**: `asyncio.gather` with `RateLimiter` (semaphore + per-request delay). Playwright pages are created per-task inside the semaphore to avoid sharing. PDF extraction uses `asyncio.to_thread` since pdfplumber is CPU-bound.
