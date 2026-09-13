import sys
import os
import json
import re
from urllib.parse import urlparse
from html.parser import HTMLParser

class ContentExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script_style_nav = 0
        self.text_content = []
        self.headings = []
        self.meta_description = ""
        self.json_ld_names = []
        self.in_json_ld = False
        self.json_ld_buffer = ""
        self.current_heading = None
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ["script", "style", "svg", "noscript", "nav"]:
            if tag == "script" and attrs_dict.get("type") == "application/ld+json":
                self.in_json_ld = True
            else:
                self.in_script_style_nav += 1
                
        if tag in ["h1", "h2"]:
            self.current_heading = {"tag": tag, "text": ""}
            
        if tag == "meta":
            if attrs_dict.get("name", "").lower() == "description":
                self.meta_description = attrs_dict.get("content", "")
                
    def handle_endtag(self, tag):
        if tag in ["script", "style", "svg", "noscript", "nav"]:
            if tag == "script" and self.in_json_ld:
                self.in_json_ld = False
                try:
                    data = json.loads(self.json_ld_buffer)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if "@graph" in item and isinstance(item["@graph"], list):
                            for g in item["@graph"]:
                                if "name" in g:
                                    self.json_ld_names.append(g["name"])
                        else:
                            if "name" in item:
                                self.json_ld_names.append(item["name"])
                except:
                    pass
                self.json_ld_buffer = ""
            else:
                self.in_script_style_nav = max(0, self.in_script_style_nav - 1)
                
        if tag in ["h1", "h2"] and self.current_heading:
            self.headings.append(self.current_heading)
            self.current_heading = None

    def handle_data(self, data):
        if self.in_json_ld:
            self.json_ld_buffer += data
        elif self.in_script_style_nav == 0:
            text = data.strip()
            if text:
                self.text_content.append(text)
                if self.current_heading:
                    self.current_heading["text"] += text + " "

def audit(url, source_file=None):
    if not source_file or not os.path.exists(source_file):
        return []
        
    with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
        
    extractor = ContentExtractor()
    extractor.feed(html)
    
    full_text = " ".join(extractor.text_content)
    # Normalize whitespace
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    words = full_text.split()[:300]
    first_300_words = " ".join(words)
    
    clean_headings = []
    for h in extractor.headings:
        if h["text"].strip():
            clean_headings.append({h["tag"]: h["text"].strip()})
            
    payload = {
        "domain": urlparse(url).netloc,
        "meta_description": extractor.meta_description,
        "json_ld_entities": list(set(extractor.json_ld_names)),
        "headings": clean_headings,
        "visible_text_snippet": first_300_words
    }
    
    out_dir = os.path.dirname(source_file)
    out_file = os.path.join(out_dir, "extracted_content.json")
    with open(out_file, "w", encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
        
    return []

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
