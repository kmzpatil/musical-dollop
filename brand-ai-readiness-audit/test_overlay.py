import sys
sys.path.append('.')
from skills.shared.parser import parse_html
html = '<div aria-modal="true" class="xyz-123">Content</div>'
result = parse_html(html)
if result["parser"].has_overlay:
    print("✅ aria-modal detection active.")
else:
    print("❌ Failed")
