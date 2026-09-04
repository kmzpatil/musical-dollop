import sys
import os
import json
import re

# Add the marketplace root to sys.path to import the shared parser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from skills.shared.parser import parse_url, parse_html

def audit(url, source_file=None):
    findings = []
    
    if source_file and os.path.exists(source_file):
        with open(source_file, 'r') as f:
            html = f.read()
        result = parse_html(html)
    else:
        result = parse_url(url)
        
    if not result["success"]:
        return findings

    parser = result["parser"]
    
    title = parser.title.strip() if getattr(parser, 'title', None) else ""
    if not title:
        brand = url.split("://")[-1].split("/")[0].replace("www.", "").split(".")[0]
    else:
        parts = re.split(r'[-|]', title)
        brand = parts[-1].strip() if parts else title.strip()
    
    body_text = ""
    for el in parser.elements:
        if el["text"]:
            body_text += el["text"] + " "
    
    words = body_text.split()[:100]
    first_100 = " ".join(words).lower()
    brand_lower = brand.lower()
    
    definitional_verbs = ["is a", "provides", "develops", "creates", "delivers", "offers"]
    
    found_definition = False
    if brand_lower in first_100:
        for verb in definitional_verbs:
            if verb in first_100:
                found_definition = True
                break
                
    if not found_definition:
        findings.append({
            "id": "A-001",
            "title": "Entity Definition Buried or Missing",
            "severity": "high",
            "evidence": f"The brand entity '{brand}' and definitional verbs do not appear within the first 100 words of the parsed body text.",
            "impact": 4,
            "effort": 2,
            "suggested_action": {
                "summary": "Ensure the first paragraph of the page clearly states what the brand is and what it provides. LLMs struggle to extract concise summaries when definitions are buried deep in the DOM or hidden in unstructured layouts.",
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
