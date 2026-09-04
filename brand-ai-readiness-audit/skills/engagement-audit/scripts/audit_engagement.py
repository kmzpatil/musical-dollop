import sys
import os
import json

# Add the marketplace root to sys.path to import the shared parser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from skills.shared.parser import parse_url, parse_html
from urllib.parse import urlparse

def audit(url, source_file=None):
    findings = []
    
    if source_file and os.path.exists(source_file):
        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        result = parse_html(html)
    else:
        result = parse_url(url)
        
    if not result["success"]:
        return findings

    parser = result["parser"]

    # 1. Orientation / Value Proposition Checks
    if not parser.has_nav and not parser.has_header:
        findings.append({
            "id": "E-001",
            "title": "Weak Above-the-Fold Visibility",
            "severity": "medium",
            "evidence": "No <nav> or <header> tags found in the HTML structure to orient the user.",
            "impact": 3,
            "effort": 4,
            "suggested_action": {
                "summary": "Implement semantic <nav> and <header> elements to provide clear context and navigation for incoming visitors. LLMs use these landmarks to quickly parse site taxonomy and establish context.",
                "priority": "medium"
            }
        })

    # 2. Internal Linking & Depth
    parsed_base = urlparse(url)
    base_domain = parsed_base.netloc
    
    internal_links = 0
    for link in parser.links:
        parsed_link = urlparse(link)
        if not parsed_link.netloc or parsed_link.netloc == base_domain:
            internal_links += 1

    if internal_links < 3 and parser.buttons == 0:
        findings.append({
            "id": "E-002",
            "title": "Navigation Path Depth & Dead Ends",
            "severity": "high",
            "evidence": f"Found only {internal_links} internal links and {parser.buttons} buttons. This suggests a dead end.",
            "impact": 4,
            "effort": 3,
            "suggested_action": {
                "summary": "Add clear Call-to-Action (CTA) buttons or internal links to engage visitors and reduce click distance to key info. Dead ends severely impact user retention metrics, which AI agents increasingly track to score authority.",
                "priority": "high"
            }
        })

    # 3. Mobile Readiness
    if not parser.has_viewport:
        findings.append({
            "id": "E-003",
            "title": "Missing Mobile Viewport Meta Tag",
            "severity": "critical",
            "evidence": "No <meta name='viewport'> tag found.",
            "impact": 5,
            "effort": 5,
            "suggested_action": {
                "summary": "Add a viewport meta tag (e.g. <meta name='viewport' content='width=device-width, initial-scale=1'>) for mobile responsiveness. Search algorithms universally penalize desktop-only rendering.",
                "priority": "critical"
            }
        })
        
    # 4. DOM Complexity
    if parser.max_dom_depth > 20:
        findings.append({
            "id": "E-004",
            "title": "Excessive DOM Depth",
            "severity": "medium",
            "evidence": f"Maximum DOM depth is {parser.max_dom_depth}. Excessive nesting harms performance and complicates LLM parsing.",
            "impact": 3,
            "effort": 2,
            "suggested_action": {
                "summary": "Flatten the HTML structure to improve rendering performance and simplify context extraction for AI crawlers. Deep DOMs exhaust crawler time-budgets and dilute semantic signals.",
                "priority": "medium"
            }
        })
        
    # 5. Semantic Content Containers
    if not parser.has_main_or_article:
        findings.append({
            "id": "E-005",
            "title": "Missing Semantic Content Area",
            "severity": "high",
            "evidence": "No <main> or <article> tags found. AI crawlers struggle to distinguish primary content from sidebar noise.",
            "impact": 4,
            "effort": 2,
            "suggested_action": {
                "summary": "Wrap the primary page content in a <main> or <article> tag. Machines extract facts more reliably when explicit plain text is separated from navigational or advertorial layout elements.",
                "priority": "high"
            }
        })
        
    # 6. Heading Hierarchy
    if parser.h1_count != 1:
        findings.append({
            "id": "E-006",
            "title": "Broken Heading Hierarchy (H1)",
            "severity": "high",
            "evidence": f"Found {parser.h1_count} <h1> tags. There should be exactly 1 to ground the page topic.",
            "impact": 5,
            "effort": 1,
            "suggested_action": {
                "summary": "Ensure exactly one highly descriptive <h1> tag is present on the page. Multiple H1s force the parser to guess the primary topic, increasing the risk of entity misattribution.",
                "priority": "high"
            }
        })

    # 7. Intrusive Overlay Detection
    if getattr(parser, 'has_overlay', False):
        findings.append({
            "id": "E-007",
            "title": "Intrusive Overlay Detected",
            "severity": "high",
            "evidence": "Detected modal, popup, cookie-banner, or blocking interstitial in the DOM.",
            "impact": 5,
            "effort": 2,
            "suggested_action": {
                "summary": "AI-referred visitors may bounce due to immediate viewport obstruction. Use non-blocking banners instead of centered overlays or modals that require immediate interaction.",
                "priority": "high"
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
        
    source_file = sys.argv[2] if len(sys.argv) > 2 else None
        
    results = audit(url, source_file)
    print(json.dumps(results, indent=2))
