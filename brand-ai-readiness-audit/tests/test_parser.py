import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from skills.shared.parser import IngestionParser

class TestParser(unittest.TestCase):
    def test_void_elements_depth(self):
        p = IngestionParser()
        p.feed("<div><img><meta><br></div>")
        self.assertEqual(p.max_dom_depth, 1)

    def test_script_style_skipped(self):
        p = IngestionParser()
        p.feed("<html><body><p>Visible</p><script>Hidden</script></body></html>")
        # Ensure hidden content wasn't counted in text length
        self.assertEqual(p.body_text_length, len("Visible"))

    def test_overlay_detection(self):
        p = IngestionParser()
        p.feed("<div class='cookie-banner' role='dialog'>Accept Cookies</div>")
        self.assertTrue(p.has_overlay)

if __name__ == '__main__':
    unittest.main()
