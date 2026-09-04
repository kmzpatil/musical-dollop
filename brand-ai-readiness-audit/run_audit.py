import sys
import os
import subprocess
import argparse
from urllib.parse import urlparse

def run_audit(url, output_file=None, debug=False):
    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else url
    
    # Create structured folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(base_dir, "reports", domain)
    os.makedirs(report_dir, exist_ok=True)
    
    if debug:
        print(f"[DEBUG] Starting audit for {domain}...")
        print(f"[DEBUG] Results will be stored in {report_dir}")
    else:
        print(f"[*] Starting audit for {domain}...")
        
    # Define output files
    disc_file = os.path.join(report_dir, "discoverability.json")
    eng_file = os.path.join(report_dir, "engagement.json")
    final_file = output_file if output_file else os.path.join(report_dir, "final_report.json")
    source_file = os.path.join(report_dir, "source.html")
    
    # Fetch HTML once
    if debug:
        print(f"[DEBUG] Fetching URL {url}...")
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        with open(source_file, "w", encoding='utf-8') as f:
            f.write(html)
            
        # Generate LLM Markdown View
        import sys
        sys.path.append(base_dir)
        from skills.shared.parser import parse_html
        result = parse_html(html)
        md_file = os.path.join(report_dir, "llm_view.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(result["parser"].to_markdown())
            
    except Exception as e:
        print(f"[!] Failed to fetch {url}: {e}")
        with open(source_file, "w", encoding='utf-8') as f:
            f.write("")
        md_file = ""
            
    def run_skill(name, script_path, args, out_path):
        if debug:
            print(f"[DEBUG] Running {name}...")
        else:
            print(f"  -> Running {name}...")
            
        with open(out_path, "w") as out_file:
            res = subprocess.run(["python", script_path] + args, stdout=out_file, cwd=base_dir)
            if res.returncode != 0:
                print(f"[!] {name} failed with exit code {res.returncode}. Proceeding with partial data.")
                
    run_skill("discoverability-audit", "skills/discoverability-audit/scripts/audit_discoverability.py", [url, source_file], disc_file)
    run_skill("engagement-audit", "skills/engagement-audit/scripts/audit_engagement.py", [url, source_file], eng_file)
    
    ai_ans_file = os.path.join(report_dir, "ai_answerability.json")
    run_skill("ai-answerability-audit", "skills/ai-answerability-audit/scripts/extract_facts.py", [url, source_file], ai_ans_file)
        
    # Run orchestrator
    if debug:
        print("[DEBUG] Running audit-orchestrator...")
    else:
        print("  -> Running audit-orchestrator...")
        
    orchestrator_args = ["python", "skills/audit-orchestrator/scripts/orchestrate.py", url, disc_file, eng_file, ai_ans_file]
    with open(final_file, "w") as out_file:
        res = subprocess.run(orchestrator_args, stdout=out_file, cwd=base_dir)
        if res.returncode != 0:
            print(f"[!] Orchestrator failed with exit code {res.returncode}.")
            
    print(f"[*] Audit complete! Final report saved to: {final_file}")
    
    # Print beautiful summary
    if os.path.exists(final_file) and not debug:
        import json
        with open(final_file, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
            
        print("\n" + "="*50)
        print(f" AUDIT COMPLETE: {final_data.get('site', url)}")
        print("="*50)
        
        summary = final_data.get("summary", {})
        print(f" Total Findings: {summary.get('total_findings', 0)}")
        print(f" [ Critical: {summary.get('critical', 0)} | High: {summary.get('high', 0)} | Medium: {summary.get('medium', 0)} | Low: {summary.get('low', 0)} ]\n")
        
        for finding in final_data.get("findings", []):
            sev = finding.get("severity", "").upper()
            title = finding.get("title", "")
            print(f" - [{sev}] {title}")
            
        print("\n" + "="*50)
        print(f" Full JSON report saved to: {final_file}")
        try:
            if md_file:
                print(f" LLM Markdown View saved to: {md_file}")
        except:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Brand AI-Readiness Audit")
    parser.add_argument("url", help="Target URL to audit")
    parser.add_argument("--output", help="Optional file path for the final JSON report")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    
    args = parser.parse_args()
    
    target_url = args.url
    if not target_url.startswith("http"):
        target_url = "https://" + target_url
        
    run_audit(target_url, output_file=args.output, debug=args.debug)
