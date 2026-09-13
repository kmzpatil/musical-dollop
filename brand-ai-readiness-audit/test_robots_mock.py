import urllib.robotparser
from unittest.mock import patch, MagicMock
from skills.shared.parser import parse_url, parse_html
import sys
sys.path.append('.')
from skills.discoverability_audit.scripts.audit_discoverability import check_robots

# Can't do this easily because it requires importing check_robots which I already have but path might be tricky. Let's write a simple HTTP server instead.
