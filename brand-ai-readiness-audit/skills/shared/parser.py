import urllib.request
import time
import json
from html.parser import HTMLParser

class IngestionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.current_depth = 0
        self.tag_stack = []
        
        self.has_json_ld = False
        self.has_same_as = False
        self.in_json_ld = False
        self.json_ld_content = ""
        self.json_ld_types = []
        
        self.title = ""
        self.in_title = False
        self.meta_description = ""
        
        # UX & Semantic landmarks
        self.has_nav = False
        self.has_header = False
        self.links = []
        self.buttons = 0
        self.has_viewport = False
        
        # Advanced skill level metrics
        self.og_tags = 0
        self.og_title = False
        self.og_description = False
        self.max_dom_depth = 0
        self.has_canonical = False
        self.h1_count = 0
        self.has_main_or_article = False
        
        # Image flags
        self.images_without_alt = 0
        
        # JS Proxy Check
        self.body_text_length = 0
        self.has_root_div = False
        self.has_noscript = False

    def handle_starttag(self, tag, attrs):
        self.current_depth += 1
        if self.current_depth > self.max_dom_depth:
            self.max_dom_depth = self.current_depth
            
        self.tag_stack.append(tag)
        attrs_dict = dict(attrs)
        
        if tag == "script" and attrs_dict.get("type") == "application/ld+json":
            self.has_json_ld = True
            self.in_json_ld = True
        elif tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            if name == "description":
                self.meta_description = attrs_dict.get("content", "")
            elif name == "viewport":
                self.has_viewport = True
            elif prop.startswith("og:") or name.startswith("twitter:"):
                self.og_tags += 1
                if prop == "og:title":
                    self.og_title = True
                elif prop == "og:description":
                    self.og_description = True
        elif tag == "link" and attrs_dict.get("rel") == "canonical":
            self.has_canonical = True
        elif tag == "nav":
            self.has_nav = True
        elif tag == "header":
            self.has_header = True
        elif tag in ["main", "article"]:
            self.has_main_or_article = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "a" and "href" in attrs_dict:
            self.links.append(attrs_dict["href"])
        elif tag == "button":
            self.buttons += 1
        elif tag == "img":
            alt = attrs_dict.get("alt", None)
            if alt is None or alt.strip() == "":
                self.images_without_alt += 1
        elif tag == "div" and attrs_dict.get("id") in ["root", "app"]:
            self.has_root_div = True
        elif tag == "noscript":
            self.has_noscript = True
                
        # Record structural element
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "li", "div", "span"]:
            self.elements.append({
                "type": tag,
                "depth": self.current_depth,
                "text": "",
                "attributes": attrs_dict
            })

    def handle_endtag(self, tag):
        self.current_depth -= 1
        if self.tag_stack:
            self.tag_stack.pop()
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.in_json_ld:
            self.in_json_ld = False
            # Parse JSON-LD for sameAs and schema types
            try:
                data = json.loads(self.json_ld_content)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if "sameAs" in item:
                        self.has_same_as = True
                    schema_type = item.get("@type", "")
                    if schema_type:
                        self.json_ld_types.append({
                            "type": schema_type,
                            "has_offers": "offers" in item,
                            "has_same_as": "sameAs" in item
                        })
            except Exception:
                pass
            self.json_ld_content = "" # reset for next script tag

    def handle_data(self, data):
        text = data.strip()
        if self.in_title:
            self.title += text
            
        if self.in_json_ld:
            self.json_ld_content += data
            
        if text and self.elements and "script" not in self.tag_stack and "style" not in self.tag_stack:
            # Append text to the last opened structural element
            self.elements[-1]["text"] += text + " "
            
        if text and "script" not in self.tag_stack and "style" not in self.tag_stack:
            self.body_text_length += len(text)

    def to_markdown(self):
        md = []
        md.append(f"# {self.title}\n")
        if self.meta_description:
            md.append(f"> {self.meta_description}\n")
        
        for el in self.elements:
            text = el["text"].strip()
            if not text:
                continue
                
            tag = el["type"]
            if tag == "h1":
                md.append(f"# {text}")
            elif tag == "h2":
                md.append(f"## {text}")
            elif tag == "h3":
                md.append(f"### {text}")
            elif tag == "h4":
                md.append(f"#### {text}")
            elif tag == "h5":
                md.append(f"##### {text}")
            elif tag == "h6":
                md.append(f"###### {text}")
            elif tag == "li":
                md.append(f"- {text}")
            elif tag in ["p", "div", "span"]:
                md.append(f"{text}")
                
        return "\n\n".join(md)

def parse_url(url, retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    }
    
    last_error = None
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
            parser = IngestionParser()
            parser.feed(html)
            return {"success": True, "html_length": len(html), "parser": parser}
        except Exception as e:
            last_error = str(e)
            time.sleep(2 ** attempt) # Exponential backoff
            
    return {"success": False, "error": last_error}
