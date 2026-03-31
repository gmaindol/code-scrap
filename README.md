Knowledge Ingestion Pipeline for NotebookLM
📌 Project Overview
This project is an automated Knowledge Ingestion Pipeline designed to rapidly aggregate technical and marketing intelligence from a target company's website.

It was specifically built to bypass the 50-source upload limit of Google's NotebookLM. Instead of manually uploading dozens of individual links or PDFs, this pipeline crawls a target website, extracts the raw text from web pages and whitepapers, strips away the web noise (like navigation bars and footers), and compiles everything into a single, massive Markdown (.md) file. This single file can then be uploaded to NotebookLM to create an instant, comprehensive AI knowledge base about the company.

The Challenge
Scraping modern corporate websites is complex due to three main factors:

Dynamic JavaScript Rendering: Modern sites (built on React, Vue, etc.) do not load their text in the initial HTML request. Traditional scrapers see a blank page.

Format Variety: High-value technical data is often split between standard HTML documentation and downloadable PDF whitepapers.

Navigation Brittleness: Trying to write a script that "clicks" through pagination on a blog often breaks when the website updates its UI.

⚙️ How It Works: The Architecture
To solve the challenges above, this pipeline operates in three distinct phases:

Phase 1: Sitemap Discovery (The Map)
Instead of guessing where content lives or scraping brittle pagination, the script points directly to the target company's sitemap.xml.

It parses the XML map to find every single URL the company has published.

It applies a Keyword Filter (e.g., /blog/, /docs/, .pdf) to drop irrelevant pages like "Contact Us" or "Careers," ensuring only high-signal knowledge is retained.

Phase 2: The Content Router (The Engine)
Once the list of URLs is generated, the script loops through them and routes each URL to the appropriate extraction engine based on its file type:

PDF Extractor (pdfplumber): If the URL ends in .pdf, the script downloads the file securely into the system's temporary memory (RAM), extracts the raw text, and discards the file. This prevents your hard drive from filling up with random whitepapers.

HTML Extractor (Playwright & BeautifulSoup): If the URL is a standard web page, the script spins up a headless Chromium browser using Playwright. It waits for the network to settle (ensuring dynamic JavaScript has loaded the text), grabs the HTML, and uses BeautifulSoup to strip out headers, footers, and scripts.

Phase 3: Compilation (The Output)
As each page or PDF is extracted, the text is formatted cleanly and appended to a single output file (NotebookLM_Knowledge_Base.md).

Each section is automatically prepended with ## Source URL: [The URL] so that when NotebookLM generates an answer, it can accurately cite the specific blog post or whitepaper the information came from.

The final result is a clean, text-only Markdown document ready for AI ingestion.