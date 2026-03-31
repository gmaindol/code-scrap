# GitHub Push Guide

Step-by-step instructions to push your code-scrap pipeline to GitHub.

---

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Enter repository name: `code-scrap` (or your preferred name)
3. Add description: "Async web scraper for building NotebookLM knowledge bases"
4. Choose visibility:
   - **Public** — If you want others to use it
   - **Private** — If you want to keep it for yourself
5. Click **Create repository**

Copy the repository URL (you'll need it in Step 3).

---

## Step 2: Verify .gitignore

The `.gitignore` file has been created to exclude:
- ❌ Generated markdown files (`*-knowledge-base*.md`)
- ❌ Cache files (`.codescrap_cache.json`)
- ❌ Downloaded images (`assets/`)
- ❌ Virtual environment (`.venv/`)
- ❌ Python cache (`__pycache__`)
- ❌ IDE configs (`.vscode`, `.idea`)

**Verify it's in place:**
```bash
cat .gitignore
```

---

## Step 3: Check Current Git Status

```bash
git status
```

You should see something like:
```
On branch main
Changes not staged for commit:
  modified:   ...
Untracked files:
  .gitignore
  CLAUDE.md
  USER_GUIDE.md
  README.md
  main.py
  codescrap/
  ...
```

Notice that `assets/`, `*.md` files, and `.venv/` are NOT listed (they're in `.gitignore`).

---

## Step 4: Stage Files for Commit

Add only the source code files:

```bash
git add -A
```

**Verify what will be committed:**
```bash
git status
```

You should NOT see:
- ❌ `koi-knowledge-base_part1.md`
- ❌ `koi-knowledge-base_part2.md`
- ❌ `assets/`
- ❌ `.venv/`

You SHOULD see:
- ✅ `.gitignore`
- ✅ `codescrap/` (all modules)
- ✅ `main.py`
- ✅ `pyproject.toml`
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `CLAUDE.md`
- ✅ `USER_GUIDE.md`

---

## Step 5: Create Initial Commit

```bash
git commit -m "Initial commit: Add code-scrap web scraping pipeline

- Async sitemap-based URL discovery with index recursion
- Multi-format extraction (HTML, PDF, OpenAPI specs)
- Image download and table-to-markdown conversion
- Rate limiting with exponential backoff and retry logic
- URL caching for resumable runs
- Automatic output chunking for NotebookLM
- Full CLI with configurable keywords, concurrency, rate limits
- Comprehensive documentation (README, USER_GUIDE, CLAUDE)"
```

---

## Step 6: Add Remote Repository

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repo name:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

**Verify:**
```bash
git remote -v
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git (fetch)
origin  https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git (push)
```

---

## Step 7: Push to GitHub

Push your code to the main branch:

```bash
git branch -M main
git push -u origin main
```

**Expected output:**
```
Enumerating objects: ...
Counting objects: ...
Compressing objects: ...
Writing objects: ...
remote: ...
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## Step 8: Verify on GitHub

1. Go to `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
2. You should see all your source files
3. No `*.md` files from scrapes or `assets/` folder should be visible

---

## Future Commits

After development, commit and push like this:

```bash
# Make changes to code
# ...

# Check what changed
git status

# Stage changes
git add codescrap/

# Commit
git commit -m "Feature: Add X, fix bug Y"

# Push
git push origin main
```

---

## Optional: Add GitHub Metadata

### Add Topics

On GitHub repository page → Settings → Topics, add:
- `web-scraping`
- `notebooklm`
- `async`
- `knowledge-base`
- `ai`

### Add License

Add a `LICENSE` file to your repo:

**Option A: MIT License** (recommended for open source)

```bash
curl -s https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/licenses/mit.txt > LICENSE
git add LICENSE
git commit -m "Add MIT license"
git push origin main
```

**Option B: Create manually in GitHub** (Settings → License)

---

## Quick Reference: Complete Workflow

```bash
# 1. Create .gitignore (already done)
cat .gitignore

# 2. Check what will be pushed
git status

# 3. Stage all files
git add -A

# 4. Commit
git commit -m "Initial commit: code-scrap pipeline"

# 5. Add remote (replace with your GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/code-scrap.git

# 6. Push to GitHub
git push -u origin main

# 7. Verify on GitHub
# Visit: https://github.com/YOUR_USERNAME/code-scrap
```

---

## Troubleshooting

### "fatal: not a git repository"

If you get this error, you need to initialize git:

```bash
git init
git add .gitignore
git commit -m "Initial commit"
```

Then proceed with steps 6-7.

---

### "fatal: remote origin already exists"

If git remote already exists, update it:

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/code-scrap.git
git push -u origin main
```

---

### ".gitignore not working (files still being tracked)"

If files were committed before `.gitignore` was added, remove them from tracking:

```bash
git rm --cached koi-knowledge-base*.md
git rm --cached KOI_SCRAPE_REPORT.md
git rm --cached .codescrap_cache.json
git rm -r --cached assets/
git commit -m "Stop tracking generated files"
git push origin main
```

---

### Authentication Issues (HTTPS)

If you get authentication errors, use a GitHub Personal Access Token (PAT):

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Create a new token with `repo` scope
3. Use token as password when prompted

Or use SSH (simpler long-term):

```bash
# Generate SSH key (if not already done)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to GitHub Settings → SSH and GPG keys

# Update remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/code-scrap.git
git push -u origin main
```

---

## What Gets Pushed

✅ **Source Code:**
- `codescrap/` — All modules
- `main.py` — Entry point
- `pyproject.toml` — Project metadata
- `requirements.txt` — Dependencies

✅ **Documentation:**
- `README.md` — Project overview
- `USER_GUIDE.md` — How to use
- `CLAUDE.md` — Technical details
- `.gitignore` — Ignore patterns
- `LICENSE` — License info

❌ **NOT Pushed:**
- `koi-knowledge-base*.md` — Generated content
- `assets/` — Downloaded images
- `.codescrap_cache.json` — Local cache
- `.venv/` — Virtual environment
- `__pycache__/` — Python cache

---

## Next Steps

1. **Clone on another machine:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/code-scrap.git
   cd code-scrap
   pip install -r requirements.txt
   playwright install chromium
   python main.py --sitemap-url https://example.com/sitemap.xml
   ```

2. **Invite collaborators** (if desired)

3. **Add GitHub Actions** for CI/CD (optional)

4. **Create releases** when you have stable versions

---

Happy deploying! 🚀
