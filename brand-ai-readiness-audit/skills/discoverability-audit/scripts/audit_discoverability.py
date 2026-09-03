import sys
import os
import json
import urllib.request
from urllib.parse import urlparse

# Add the marketplace root to sys.path to import the shared parser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from skills.shared.parser import parse_url

def check_robots(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    blocked_bots = []
    try:
        req = urllib.request.Request(robots_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode('utf-8')
            lines = content.split('\n')
            current_agent = ""
            for line in lines:
                line = line.strip().lower()
                if line.startswith('user-agent:'):
                    current_agent = line.split(':')[1].strip()
                elif line.startswith('disallow:') and '/' in line:
                    if current_agent in ['gptbot', 'claudebot', 'perplexitybot', 'oai-searchbot', 'ccbot', 'google-extended']:
                        blocked_bots.append(current_agent)
                        
            if blocked_bots:
                return False, f"Robots.txt is explicitly blocking AI crawlers: {', '.join(set(blocked_bots))}."
            return True, "Robots.txt is present and does not block known AI crawlers."
    except Exception:
        return True, "No restrictive robots.txt found."

def check_llms_txt(url):
    parsed = urlparse(url)
    llms_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"
    try:
        req = urllib.request.Request(llms_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.getcode() == 200:
                return True
    except Exception:
        pass
    return False

def audit(url):
    findings = []
    
    # 1. Robots check for AI Crawlers
    is_crawlable, evidence = check_robots(url)
    if not is_crawlable:
        findings.append({
            "id": "D-001",
            "title": "AI Crawlers Blocked in Robots.txt",
            "severity": "critical",
            "evidence": evidence,
            "impact": 5,
            "effort": 1,
            "suggested_action": {
                "summary": "Update robots.txt to allow specific AI bots like GPTBot, ClaudeBot, and PerplexityBot to read your public content. Generative AI engines require explicit permission to ingest your brand's facts into their training weights or real-time indexes.",
                "priority": "critical"
            }
        })
        
    # 2. llms.txt check
    has_llms_txt = check_llms_txt(url)
    if not has_llms_txt:
        findings.append({
            "id": "D-008",
            "title": "Missing llms.txt",
            "severity": "medium",
            "evidence": "No llms.txt found at the domain root.",
            "impact": 4,
            "effort": 1,
            "suggested_action": {
                "summary": "Adopt the llms.txt standard by hosting an llms.txt file to provide structured context explicitly for AI crawlers. Machines extract facts more reliably from explicit, concise markdown than from complex HTML layouts.",
                "priority": "high"
            }
        })

    # Fetch and parse using the unified Ingestion Engine
    result = parse_url(url)
    if not result["success"]:
        findings.append({
            "id": "D-000",
            "title": "Page Load Failure",
            "severity": "critical",
            "evidence": f"Failed to load {url}: {result.get('error')}",
            "impact": 5,
            "effort": 3,
            "suggested_action": {
                "summary": "Ensure the server is running and accessible or unblock the crawler headers.",
                "priority": "critical"
            }
        })
        return findings

    parser = result["parser"]

    # 3. JSON-LD check
    if not parser.has_json_ld:
        example_json_ld = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": parser.title if parser.title else "Your Brand Name",
            "url": url,
            "sameAs": ["https://en.wikipedia.org/wiki/Your_Brand"]
        }
        findings.append({
            "id": "D-002",
            "title": "Missing JSON-LD Structured Data",
            "severity": "high",
            "evidence": "No <script type='application/ld+json'> found in the initial HTML payload.",
            "impact": 4,
            "effort": 3,
            "suggested_action": {
                "summary": "Add Schema.org JSON-LD to describe the organization, products, or articles clearly. AI assistants rely on structured data to confidently extract semantic entities without guessing.",
                "priority": "high",
                "snippet": f"<script type=\"application/ld+json\">\n{json.dumps(example_json_ld, indent=2)}\n</script>"
            }
        })
    else:
        # Schema-type-aware completeness check
        for schema in parser.json_ld_types:
            stype = schema["type"]
            if stype == "Product" and not schema["has_offers"]:
                findings.append({
                    "id": "D-011",
                    "title": "Incomplete Product Schema (Missing Offers)",
                    "severity": "medium",
                    "evidence": "JSON-LD Product schema is present but missing the 'offers' property (pricing).",
                    "impact": 4,
                    "effort": 2,
                    "suggested_action": {
                        "summary": "Populate the 'offers' property. LLMs will refuse to confidently state a product's price without explicit structured validation.",
                        "priority": "high"
                    }
                })
            elif stype == "Organization" and not schema["has_same_as"]:
                findings.append({
                    "id": "D-012",
                    "title": "Incomplete Organization Schema (Missing sameAs)",
                    "severity": "medium",
                    "evidence": "JSON-LD Organization schema is present but missing the 'sameAs' property.",
                    "impact": 4,
                    "effort": 2,
                    "suggested_action": {
                        "summary": "Add 'sameAs' links to Wikipedia, LinkedIn, etc. Generative engines use this graph to disambiguate your entity from similarly named companies.",
                        "priority": "high"
                    }
                })

        if not parser.has_same_as:
            findings.append({
                "id": "D-009",
                "title": "Entity Ambiguity (Missing sameAs)",
                "severity": "high",
                "evidence": "JSON-LD structured data is present but lacks a 'sameAs' property pointing to known entities like Wikipedia or Wikidata.",
                "impact": 4,
                "effort": 2,
                "suggested_action": {
                    "summary": "Add 'sameAs' links to disambiguate your brand identity and anchor it to recognized knowledge bases. AI hallucination often stems from entity confusion.",
                    "priority": "high"
                }
            })

    # 4. Accessibility / Alt text
    if parser.images_without_alt > 0:
         findings.append({
            "id": "D-005",
            "title": "Images Missing Alt Text",
            "severity": "medium",
            "evidence": f"Found {parser.images_without_alt} images without alt text. LLMs are blind to these images.",
            "impact": 3,
            "effort": 2,
            "suggested_action": {
                "summary": "Ensure all critical images have descriptive alt text for accessibility and AI parsing. Vision models use surrounding text and alt tags to contextualize non-textual content.",
                "priority": "medium"
            }
        })

    # 5. JS-Render Proxy Check
    if parser.body_text_length < 500 and (parser.has_root_div or parser.has_noscript):
        findings.append({
            "id": "D-010",
            "title": "High JavaScript Dependency",
            "severity": "critical",
            "evidence": f"Low text-to-markup ratio + SPA root detected. Raw HTML body contains only {parser.body_text_length} characters of text. AI crawlers that don't execute JS will see a blank page.",
            "impact": 5,
            "effort": 5,
            "suggested_action": {
                "summary": "Implement Server-Side Rendering (SSR) or dynamic rendering to serve populated HTML directly to AI crawlers. Search engines heavily deprioritize pages that require full client-side JavaScript execution to reveal primary content.",
                "priority": "critical"
            }
        })
        
    # 6. Canonical Tags
    if not parser.has_canonical:
        findings.append({
            "id": "D-007",
            "title": "Missing Canonical Tag",
            "severity": "medium",
            "evidence": "No <link rel='canonical'> tag found.",
            "impact": 3,
            "effort": 1,
            "suggested_action": {
                "summary": "Add a canonical tag to prevent AI indexes from splitting your domain's entity authority across duplicate URLs. Explicit signals guide the model's weight attribution to the correct primary source.",
                "priority": "medium"
            }
        })

    return findings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[]")
        sys.exit(0)
    
    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url
        
    results = audit(url)
    print(json.dumps(results, indent=2))
