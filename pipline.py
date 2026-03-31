import time
import requests
import io
import pdfplumber
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# --- Configuration ---
SITEMAP_URL = "https://www.example-acquired-company.com/sitemap.xml"
OUTPUT_FILE = "NotebookLM_Knowledge_Base.md"

# Keywords to filter the sitemap. We don't want the "Careers" or "Contact Us" pages.
TARGET_KEYWORDS = ["/blog/", "/docs/", "/whitepaper/", "/resources/"]

# --- 1. Sitemap Discovery Layer ---
def fetch_urls_from_sitemap(sitemap_url, keywords):
    """
    Parses a sitemap.xml to extract URLs that match our target keywords.
    """
    print(f"Fetching sitemap: {sitemap_url}")
    target_urls = []
    
    try:
        # Use a standard user-agent to avoid basic bot blocks
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()
        
        # Parse as XML
        soup = BeautifulSoup(response.content, 'lxml-xml')
        
        # Find all <loc> tags which contain the URLs
        all_locs = soup.find_all('loc')
        
        for loc in all_locs:
            url = loc.text.strip()
            # If the URL contains any of our target keywords OR is a PDF, keep it
            if any(keyword in url for keyword in keywords) or url.endswith('.pdf'):
                target_urls.append(url)
                
        print(f"Discovered {len(target_urls)} relevant URLs from the sitemap.")
        return list(set(target_urls)) # Return unique URLs
        
    except Exception as e:
        print(f"Failed to fetch or parse sitemap: {e}")
        return []

# --- 2. Extraction Modules ---
def clean_html_to_markdown(html_content, url):
    """Parses dynamic HTML, removes noise, and converts to Markdown."""
    soup = BeautifulSoup(html_content, 'html.parser')

    for element in soup(["nav", "footer", "script", "style", "header", "aside"]):
        element.decompose()

    main_content = soup.find('main') or soup.find('article') or soup.body
    if not main_content:
        return ""

    text = main_content.get_text(separator='\n', strip=True)
    return f"## Source URL: {url} (HTML Webpage)\n\n{text}\n\n---\n\n"

def extract_pdf_text(pdf_url):
    """Downloads a PDF into memory and extracts its text."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pdf_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Load PDF directly into memory (bypassing the need to save it locally)
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            pdf_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text + "\n"
                    
        return f"## Source URL: {url} (PDF Whitepaper/Document)\n\n{pdf_text}\n\n---\n\n"
        
    except Exception as e:
        print(f"Failed to extract PDF {pdf_url}: {e}")
        return f"## Source URL: {pdf_url}\n*Failed to extract PDF: {e}*\n\n---\n\n"

def extract_openapi_to_markdown(api_url):
    """
    Fetches an OpenAPI/Swagger spec (JSON or YAML) and converts it to Markdown.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Many API endpoints require accepting specific content types
        headers['Accept'] = 'application/json, application/yaml, text/yaml'
        
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Determine format and parse into a Python dictionary
        content_type = response.headers.get('Content-Type', '').lower()
        if 'yaml' in content_type or api_url.endswith(('.yaml', '.yml')):
            spec = yaml.safe_load(response.text)
        else:
            # Default to JSON
            spec = json.loads(response.text)
            
        return parse_openapi_dict_to_markdown(spec, api_url)
        
    except Exception as e:
        print(f"Failed to extract OpenAPI spec {api_url}: {e}")
        return f"## Source URL: {api_url}\n*Failed to extract OpenAPI spec: {e}*\n\n---\n\n"

def parse_openapi_dict_to_markdown(spec, url):
    """
    Flattens the OpenAPI dictionary into a structured Markdown string optimized for LLMs.
    """
    md_lines = []
    md_lines.append(f"## Source URL: {url} (OpenAPI Specification)\n")
    
    # --- Extract API Info ---
    info = spec.get('info', {})
    title = info.get('title', 'API Documentation')
    version = info.get('version', '1.0')
    description = info.get('description', '')
    
    md_lines.append(f"### API Name: {title} (Version: {version})\n")
    if description:
        md_lines.append(f"{description}\n\n")
        
    # --- Extract Endpoints ---
    paths = spec.get('paths', {})
    if paths:
        md_lines.append("### Endpoints\n")
        for path, methods in paths.items():
            for method, details in methods.items():
                # Filter out non-HTTP methods or extension keys
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    continue
                    
                summary = details.get('summary', 'No summary provided')
                md_lines.append(f"#### `{method.upper()}` {path}")
                md_lines.append(f"**Summary:** {summary}")
                
                if 'description' in details:
                    md_lines.append(f"**Description:** {details['description']}")
                    
                # Extract Parameters
                parameters = details.get('parameters', [])
                if parameters:
                    md_lines.append("\n**Parameters:**")
                    for param in parameters:
                        # Handle $ref pointers gracefully by skipping them or extracting raw references
                        if '$ref' in param:
                            md_lines.append(f"- *(Reference to reusable parameter: {param['$ref']})*")
                            continue
                            
                        name = param.get('name', 'Unknown')
                        in_loc = param.get('in', 'query')
                        required = "Required" if param.get('required') else "Optional"
                        param_desc = param.get('description', '')
                        
                        md_lines.append(f"- `{name}` ({in_loc}, {required}): {param_desc}")
                        
                md_lines.append("\n") # Spacing between endpoints
                
    md_lines.append("---\n\n")
    return "\n".join(md_lines)

# --- 3. The Compilation Engine (Router) ---
def scrape_and_compile(urls, output_filename):
    """
    Iterates through URLs, routes to the correct extractor (HTML or PDF), 
    and compiles everything into a single Markdown document.
    """
    print(f"Starting extraction for {len(urls)} URLs...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()

        with open(output_filename, 'w', encoding='utf-8') as md_file:
            md_file.write("# Acquired Company Knowledge Base\n\n")

            for url in urls:
                print(f"Processing: {url}")
                
                # --- The Router ---
                if url.lower().endswith('.pdf'):
                    # Route to PDF Extractor
                    markdown_content = extract_pdf_text(url)
                    md_file.write(markdown_content)
                    print(f"Successfully appended PDF: {url}")
                    
                elif url.lower().endswith(('.json', '.yaml', '.yml')) or 'openapi' in url.lower() or 'swagger' in url.lower():
                    # Route to OpenAPI Extractor
                    markdown_content = extract_openapi_to_markdown(url)
                    md_file.write(markdown_content)
                    print(f"Successfully appended API Spec: {url}")
                    
                else:
                    # Route to HTML Playwright Extractor
                    try:
                        page.goto(url, wait_until="networkidle", timeout=30000)
                        html_content = page.content()
                        markdown_content = clean_html_to_markdown(html_content, url)
                        md_file.write(markdown_content)
                        print(f"Successfully appended Webpage: {url}")
                    except Exception as e:
                        print(f"Failed to scrape webpage {url}: {e}")
                        md_file.write(f"## Source URL: {url}\n*Failed to extract content: {e}*\n\n---\n\n")

        browser.close()
    print(f"\nCompilation complete! File saved as {output_filename}")

# --- Execution ---
if __name__ == "__main__":
    # Step 1: Discover URLs via Sitemap
    discovered_urls = fetch_urls_from_sitemap(SITEMAP_URL, TARGET_KEYWORDS)
    
    # Optional: Truncate list for testing so it doesn't take hours
    # discovered_urls = discovered_urls[:10] 
    
    if discovered_urls:
        # Step 2 & 3: Extract and Compile
        scrape_and_compile(discovered_urls, OUTPUT_FILE)
    else:
        print("No URLs found to process. Check your sitemap URL and keywords.")