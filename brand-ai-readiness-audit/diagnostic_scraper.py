import urllib.request
import urllib.error
import urllib.parse
import ssl
import time
import os
import re

# Matrix of domains to diagnose
DOMAINS = [
    "https://makemytrip.com",
    "https://nike.in",
    "https://apple.com",
    "https://takeuforward.org",
    "https://vaishnodevitraders.in",
    "https://huggingface.co"
]

# Advanced headers to mimic a modern Chrome browser and bypass basic bot mitigation
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Ch-Ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

def ensure_dir(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_title(html_body):
    """Extract the <title> tag content from the HTML body using regex."""
    match = re.search(r'<title[^>]*>(.*?)</title>', html_body, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return "N/A"

def scrape_domain(url, output_dir):
    """Perform a GET request for a domain and gather diagnostic metrics."""
    parsed_url = urllib.parse.urlparse(url)
    domain_name = parsed_url.netloc.replace("www.", "")
    
    # Prepare the request
    req = urllib.request.Request(url, headers=HEADERS)
    
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    start_time = time.time()
    
    status_code = None
    html_body = ""
    ttfb = 0
    
    try:
        # Fetch the URL
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            ttfb = (time.time() - start_time) * 1000
            status_code = response.getcode()
            html_bytes = response.read()
            html_body = html_bytes.decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        # Handle HTTP Errors gracefully (e.g., 403 Forbidden)
        ttfb = (time.time() - start_time) * 1000
        status_code = e.code
        try:
            html_bytes = e.read()
            html_body = html_bytes.decode('utf-8', errors='ignore')
        except Exception:
            html_body = str(e)
    except urllib.error.URLError as e:
        # Handle connection errors (DNS, Timeout)
        ttfb = (time.time() - start_time) * 1000
        status_code = "ERR"
        html_body = f"URLError: {e.reason}"
    except Exception as e:
        # Catch-all for any other exceptions
        ttfb = (time.time() - start_time) * 1000
        status_code = "ERR"
        html_body = str(e)
        
    # Save the raw HTML dump
    dump_filename = os.path.join(output_dir, f"{domain_name}.html")
    with open(dump_filename, 'w', encoding='utf-8') as f:
        f.write(html_body)
        
    # Extract title
    title = extract_title(html_body) if len(html_body) > 0 else "N/A"
    
    # Format a clean 100-char snippet (remove newlines)
    snippet = html_body[:100].replace('\n', ' ').replace('\r', '')
    if len(snippet) < 1:
        snippet = "N/A"
        
    return {
        'domain': domain_name,
        'status': status_code,
        'ttfb_ms': round(ttfb, 2),
        'size_bytes': len(html_body),
        'title': title[:30] + '...' if len(title) > 30 else title,
        'snippet': snippet
    }

def main():
    output_dir = "diagnostic_dumps"
    ensure_dir(output_dir)
    
    # Print table header
    print(f"{'Domain':<25} | {'Status':<6} | {'TTFB(ms)':<10} | {'Size(B)':<10} | {'Title':<32} | {'Snippet (first 100 chars)'}")
    print("-" * 175)
    
    # Iterate and scrape each domain
    for url in DOMAINS:
        result = scrape_domain(url, output_dir)
        print(f"{result['domain']:<25} | {str(result['status']):<6} | {result['ttfb_ms']:<10} | {result['size_bytes']:<10} | {result['title']:<32} | {result['snippet']}")

if __name__ == '__main__':
    main()
