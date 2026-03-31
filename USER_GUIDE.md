# code-scrap User Guide

Complete step-by-step guide to scrape any website and build a NotebookLM knowledge base.

---

## Table of Contents
1. [Installation](#installation)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [Step-by-Step Tutorial](#step-by-step-tutorial)
4. [Common Commands](#common-commands)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)

---

## Installation

### Step 1: Clone or Navigate to Project
```bash
cd code-scrap
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Or with uv (if you use it):
```bash
uv pip install -r requirements.txt
```

### Step 3: Install Playwright Browser
```bash
playwright install chromium
```

This downloads the headless Chromium browser needed to render JavaScript-heavy websites.

### Step 4: Verify Installation
```bash
python main.py --help
```

You should see the CLI help text. ✅ You're ready!

---

## Quick Start (5 minutes)

### The One-Liner

Replace `YOUR_SITEMAP_URL` with your target website's sitemap URL:

```bash
python main.py --sitemap-url https://example.com/sitemap.xml
```

That's it! The scraper will:
1. Discover all pages from the sitemap
2. Download and extract content from each page
3. Create `NotebookLM_Knowledge_Base.md`
4. Cache processed URLs for resumable runs

### Verify Output

```bash
ls -lh NotebookLM_Knowledge_Base*.md
```

Look for `NotebookLM_Knowledge_Base.md` (or `_part1.md`, `_part2.md` if split).

---

## Step-by-Step Tutorial

### Example: Scraping Koi.ai's Security Research

#### Step 1: Find the Target Sitemap

Most websites have a sitemap at:
- `https://example.com/sitemap.xml`
- `https://example.com/sitemap_index.xml`

For koi.ai:
```
http://www.koi.ai/sitemap.xml
```

#### Step 2: Decide What to Include

Look at the website structure and pick relevant keywords for `--keywords`:

**For technical documentation:**
```bash
--keywords /docs/ /documentation/ /guides/ /api/
```

**For blog + resources:**
```bash
--keywords /blog/ /posts/ /articles/ /resources/
```

**For security research (like koi.ai):**
```bash
--keywords /blog/ /research/
```

#### Step 3: Choose Rate Limiting Settings

- **Safe default:** `--rate-limit 1.0` (1 second between requests)
- **For stricter sites:** `--rate-limit 2.0` or `3.0`
- **For concurrent requests:** `--concurrency 2` or `3`

#### Step 4: Run the Scraper

```bash
python main.py \
  --sitemap-url http://www.koi.ai/sitemap.xml \
  --keywords /blog/ \
  --output koi-knowledge-base.md \
  --concurrency 3 \
  --rate-limit 1.0
```

#### Step 5: Monitor Progress

Watch the logs:
```
[INFO] Discovered 50 relevant URLs from sitemap
[INFO] Processing 50 URLs...
[INFO] OK: https://www.koi.ai/blog/post-1
[INFO] OK: https://www.koi.ai/blog/post-2
...
[INFO] Done! Processed 50 URLs, 0 failed.
```

#### Step 6: Upload to NotebookLM

1. Go to [NotebookLM](https://notebooklm.google.com/)
2. Create a new notebook
3. Upload the generated Markdown file(s)
4. Wait for indexing (~1-2 minutes)
5. Start asking questions!

---

## Common Commands

### Basic Scrape (Defaults)

```bash
python main.py --sitemap-url https://example.com/sitemap.xml
```

**Output:** `NotebookLM_Knowledge_Base.md`

---

### Custom Output Filename

```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --output my-docs.md
```

---

### Include Specific Sections

```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --keywords /api/ /documentation/ /guides/
```

---

### Exclude Unwanted Sections

```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --exclude /careers/ /contact/ /privacy/ /legal/
```

---

### Slower, More Conservative Scraping

For sites that are strict about rate limiting:

```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --concurrency 1 \
  --rate-limit 3.0 \
  --max-retries 5
```

**Explanation:**
- `--concurrency 1` — Only 1 page at a time
- `--rate-limit 3.0` — Wait 3 seconds between requests
- `--max-retries 5` — Retry up to 5 times on failures

---

### Faster Scraping

For sites that are fast and permissive:

```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --concurrency 5 \
  --rate-limit 0.5
```

---

### Resume a Partial Run

If scraping was interrupted, just run the same command again:

```bash
python main.py --sitemap-url https://example.com/sitemap.xml
```

It will automatically skip already-cached URLs and only process new ones.

---

### Force a Full Re-Scrape

Delete the cache and start over:

```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --clear-cache
```

---

### Custom Output Directory

```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --assets-dir ./images
```

Downloads images to `./images/` folder.

---

## Troubleshooting

### Error: "No URLs found. Check your sitemap URL and keywords."

**Solution:**
1. Verify the sitemap URL is correct:
   ```bash
   curl https://example.com/sitemap.xml
   ```
   Should return XML, not 404.

2. Adjust `--keywords` to match actual URL structure:
   ```bash
   # Try broader match
   python main.py --sitemap-url https://example.com/sitemap.xml --keywords /
   ```

3. Check `--exclude` — you might be blocking everything:
   ```bash
   python main.py --sitemap-url https://example.com/sitemap.xml --exclude /nothing/
   ```

---

### Error: "Executable doesn't exist at ... playwright ..."

**Solution:** Install Playwright browser:
```bash
playwright install chromium
```

---

### Many "FAIL" or "Retry" messages

**Cause:** Site is rate-limiting your requests.

**Solution:** Increase delays and reduce concurrency:
```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --concurrency 1 \
  --rate-limit 2.0
```

---

### Timeout Errors

**Cause:** Pages are taking too long to load (heavy JavaScript).

**Solution:** Increase max retries:
```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --max-retries 5
```

Or reduce concurrency to give pages more time:
```bash
python main.py \
  --sitemap-url https://example.com/sitemap.xml \
  --concurrency 1
```

---

### Output File is Huge (>500K chars)

**Expected behavior:** The scraper automatically splits into multiple files:
- `NotebookLM_Knowledge_Base_part1.md`
- `NotebookLM_Knowledge_Base_part2.md`
- etc.

Upload each file as a separate source in NotebookLM.

---

## Advanced Usage

### Command-Line Reference

```
python main.py [OPTIONS]

Options:
  --sitemap-url TEXT          URL of sitemap.xml (REQUIRED)
  --output TEXT               Output filename (default: NotebookLM_Knowledge_Base.md)
  --keywords TEXT             Include URLs with these keywords (space-separated)
  --exclude TEXT              Exclude URLs with these keywords (space-separated)
  --concurrency INT           Max concurrent requests (default: 5)
  --rate-limit FLOAT          Seconds between requests (default: 1.0)
  --max-retries INT           Max retries on failure (default: 3)
  --chunk-size INT            Max characters per output file (default: 480000)
  --assets-dir TEXT           Directory for downloaded images (default: assets)
  --no-cache                  Ignore existing cache, re-scrape all URLs
  --clear-cache               Clear cache before starting
  --help                      Show this help message
```

---

### Understanding the Cache

After each run, a `.codescrap_cache.json` file is created:

```json
{
  "https://example.com/page-1": {
    "timestamp": "2026-03-31T10:00:00.000000+00:00"
  },
  "https://example.com/page-2": {
    "timestamp": "2026-03-31T10:05:00.000000+00:00"
  }
}
```

This tracks which URLs have been processed. Running the scraper again skips cached URLs automatically.

**To clear:** Use `--clear-cache` or manually delete `.codescrap_cache.json`.

---

### Multiple Runs on Different Sites

Keep output separate:

```bash
# Scrape site A
python main.py --sitemap-url https://site-a.com/sitemap.xml --output site-a.md

# Scrape site B
python main.py --sitemap-url https://site-b.com/sitemap.xml --output site-b.md

# Each has its own cache
ls -la .codescrap_cache.json  # Same cache file, but you can rename it
```

**Note:** Each run overwrites the cache. If you want to keep separate caches, rename the `.codescrap_cache.json` file between runs:

```bash
python main.py --sitemap-url https://site-a.com/sitemap.xml --output site-a.md
mv .codescrap_cache.json .site-a-cache.json

python main.py --sitemap-url https://site-b.com/sitemap.xml --output site-b.md
mv .codescrap_cache.json .site-b-cache.json
```

---

### Optimizing for Different Site Types

#### For API Documentation Sites
```bash
python main.py \
  --sitemap-url https://api-docs.example.com/sitemap.xml \
  --keywords /api/ /endpoints/ /openapi/ \
  --concurrency 5 \
  --rate-limit 0.5
```

API docs are usually fast-loading and server-friendly.

#### For Blogs with Images
```bash
python main.py \
  --sitemap-url https://blog.example.com/sitemap.xml \
  --keywords /posts/ /articles/ \
  --assets-dir ./blog-images \
  --concurrency 2 \
  --rate-limit 1.5
```

Images take time to download; slower concurrency helps.

#### For Security-Sensitive Vendors
```bash
python main.py \
  --sitemap-url https://secure-site.example.com/sitemap.xml \
  --concurrency 1 \
  --rate-limit 3.0 \
  --max-retries 5
```

Conservative settings to avoid getting blocked.

---

## Real-World Example: Koi.ai

Here's the exact command that successfully scraped koi.ai's 50 blog posts:

```bash
python main.py \
  --sitemap-url http://www.koi.ai/sitemap.xml \
  --keywords /blog/ \
  --output koi-knowledge-base.md \
  --concurrency 3 \
  --rate-limit 1.0
```

**Results:**
- 50 URLs discovered and processed
- 0 failures
- Generated 2 files (482 KB total, auto-chunked)
- Completed in ~2 minutes
- Cache created for resumable runs

---

## Next Steps

1. **Find a target website** with a public sitemap
2. **Run the scraper** with appropriate settings
3. **Upload to NotebookLM** and create an AI knowledge base
4. **Ask questions** and get instant answers from the vendor's content

---

## Need Help?

See [README.md](./README.md) for architecture details or [CLAUDE.md](./CLAUDE.md) for technical implementation.

For bugs or improvements, check the project repository.

Happy scraping! 🚀
