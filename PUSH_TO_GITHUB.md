# Quick Guide: Push to GitHub

Copy-paste these commands to push your code-scrap pipeline to GitHub in 5 minutes.

---

## Prerequisites

1. **GitHub Account** — Create at [github.com](https://github.com)
2. **Git Installed** — Verify with `git --version`
3. **Create Empty Repo on GitHub** — Go to [github.com/new](https://github.com/new) and create `code-scrap`

---

## The 5-Step Push

### 1. Stage All Files

```bash
git add -A
```

**Verify nothing unwanted is staged:**
```bash
git status
```

You should see:
- ✅ `.gitignore`, `CLAUDE.md`, `USER_GUIDE.md`, `README.md`, `main.py`, `codescrap/`, etc.
- ❌ NO `koi-knowledge-base*.md`, `assets/`, `.venv/`, `__pycache__/`

### 2. Create Commit

```bash
git commit -m "Initial commit: Add code-scrap web scraping pipeline

- Async sitemap-based discovery with index recursion
- Multi-format extraction (HTML, PDF, OpenAPI)
- Image download and table conversion
- Rate limiting with backoff and retries
- URL caching for resumable runs
- Auto output chunking for NotebookLM
- Full CLI with keywords, concurrency, rate-limit config
- Complete documentation (README, USER_GUIDE, CLAUDE)"
```

### 3. Add GitHub Remote

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/code-scrap.git
```

**Verify:**
```bash
git remote -v
```

Should show:
```
origin  https://github.com/YOUR_USERNAME/code-scrap.git (fetch)
origin  https://github.com/YOUR_USERNAME/code-scrap.git (push)
```

### 4. Set Main Branch

```bash
git branch -M main
```

### 5. Push to GitHub

```bash
git push -u origin main
```

**Done!** Your repo is now on GitHub. View it at:
```
https://github.com/YOUR_USERNAME/code-scrap
```

---

## What Gets Pushed ✅

```
✅ codescrap/               (source code)
✅ main.py                  (entry point)
✅ pyproject.toml           (project config)
✅ requirements.txt         (dependencies)
✅ README.md                (overview)
✅ USER_GUIDE.md            (how to use)
✅ CLAUDE.md                (technical details)
✅ GITHUB_SETUP.md          (this file)
✅ .gitignore               (ignore patterns)
```

---

## What Does NOT Get Pushed ❌

```
❌ koi-knowledge-base*.md   (generated from scrape)
❌ assets/                  (downloaded images)
❌ .codescrap_cache.json    (local cache)
❌ .venv/                   (virtual environment)
❌ __pycache__/             (Python cache)
```

These are ignored by `.gitignore`.

---

## Troubleshooting

**"fatal: not a git repository"**
```bash
git init
git add .gitignore
git commit -m "Initial .gitignore"
# Then follow steps 1-5 above
```

**"fatal: remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/code-scrap.git
git push -u origin main
```

**GitHub asks for password**

Use a Personal Access Token (PAT):
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate token with `repo` scope
3. Use token as password

Or use SSH (better):
```bash
# Generate key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add public key to GitHub Settings → SSH and GPG keys

# Use SSH remote
git remote set-url origin git@github.com:YOUR_USERNAME/code-scrap.git
git push -u origin main
```

---

## After Pushing

### Clone on Another Machine

```bash
git clone https://github.com/YOUR_USERNAME/code-scrap.git
cd code-scrap
pip install -r requirements.txt
playwright install chromium
python main.py --sitemap-url https://example.com/sitemap.xml
```

### Future Updates

```bash
# Make changes to code
nano codescrap/cli.py

# Check changes
git status

# Stage changes
git add codescrap/

# Commit
git commit -m "Improve rate limiting logic"

# Push
git push origin main
```

---

## Optional Enhancements

### 1. Add License

```bash
# Download MIT license (popular for open source)
curl -s https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/licenses/mit.txt > LICENSE
git add LICENSE
git commit -m "Add MIT license"
git push origin main
```

### 2. Add GitHub Topics

Visit your repo on GitHub → Click **⚙ Settings** → Under "About" → Add topics:
- `web-scraping`
- `notebooklm`
- `async-python`
- `knowledge-base`

### 3. Enable GitHub Pages (Optional)

If you want documentation site:
Settings → Pages → Source: `main` → Save

Then content from `docs/` folder appears at `https://YOUR_USERNAME.github.io/code-scrap/`

---

## One-Liner (If Already Initialized)

If git is already set up, just:

```bash
git add -A && git commit -m "Initial commit" && git push -u origin main
```

---

## Status Check

```bash
# See all commits
git log --oneline

# See remote
git remote -v

# See what will push
git status
```

---

Done! Your pipeline is now on GitHub. 🚀
