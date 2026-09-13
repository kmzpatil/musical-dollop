import http.server
import socketserver
import threading
import sys
import json
import subprocess
import time

class Handler1(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if self.path == "/robots.txt":
            # Test 1: Only block /admin
            self.wfile.write(b"User-agent: GPTBot\nDisallow: /admin\n")
        else:
            self.wfile.write(b"<html><body><h1>Test1</h1></body></html>")

class Handler2(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if self.path == "/robots.txt":
            # Test 2: Block entirely
            self.wfile.write(b"User-agent: GPTBot\nDisallow: /\n")
        else:
            self.wfile.write(b"<html><body><h1>Test2</h1></body></html>")

def run_server(port, handler):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    t1 = threading.Thread(target=run_server, args=(8001, Handler1), daemon=True)
    t2 = threading.Thread(target=run_server, args=(8002, Handler2), daemon=True)
    t1.start()
    t2.start()
    time.sleep(1) # wait for servers to start
    
    print("Running Test 1 (Only /admin blocked)...")
    res1 = subprocess.run([sys.executable, "skills/discoverability-audit/scripts/audit_discoverability.py", "http://localhost:8001"], capture_output=True, text=True)
    try:
        data1 = json.loads(res1.stdout)
        d001_triggered_1 = any(f.get("id") == "D-001" for f in data1)
    except Exception as e:
        print(f"Error parsing Test 1 output: {e}\nOutput: {res1.stdout}")
        d001_triggered_1 = True
    print(f"Test 1 D-001 triggered: {d001_triggered_1}")
    
    print("Running Test 2 (Entirely blocked)...")
    res2 = subprocess.run([sys.executable, "skills/discoverability-audit/scripts/audit_discoverability.py", "http://localhost:8002"], capture_output=True, text=True)
    try:
        data2 = json.loads(res2.stdout)
        d001_triggered_2 = any(f.get("id") == "D-001" for f in data2)
    except Exception as e:
        print(f"Error parsing Test 2 output: {e}\nOutput: {res2.stdout}")
        d001_triggered_2 = False
    print(f"Test 2 D-001 triggered: {d001_triggered_2}")
    
    if not d001_triggered_1 and d001_triggered_2:
        print("✅ urllib.robotparser integration successful.")
    else:
        print("❌ Test failed!")
