import sys
import os
import subprocess
from urllib.parse import urlparse

# Import parser for markdown generation
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from skills.shared.parser import parse_url

def run_audit(url):
    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else url
    
    # Create structured folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_dir = os.path.join(base_dir, "reports", domain)
    os.makedirs(report_dir, exist_ok=True)
    
    print(f"[*] Starting audit for {domain}...")
    print(f"[*] Results will be stored in {report_dir}")
    
    # Define output files
    disc_file = os.path.join(report_dir, "discoverability.json")
    eng_file = os.path.join(report_dir, "engagement.json")
    final_file = os.path.join(report_dir, "final_report.json")
    
    # Run skills
    print("  -> Generating LLM Markdown View...")
    result = parse_url(url)
    md_file = ""
    if result["success"]:
        md_file = os.path.join(report_dir, "llm_view.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(result["parser"].to_markdown())
            
    print("  -> Running discoverability-audit...")
    subprocess.run(f'python skills/discoverability-audit/scripts/audit_discoverability.py "{url}" > "{disc_file}"', shell=True, cwd=base_dir)
    
    print("  -> Running engagement-audit...")
    subprocess.run(f'python skills/engagement-audit/scripts/audit_engagement.py "{url}" > "{eng_file}"', shell=True, cwd=base_dir)
    
    # Run orchestrator
    print("  -> Running audit-orchestrator...")
    ai_ans_file = os.path.join(report_dir, "ai_answerability.json")
    orchestrator_args = f'"{url}" "{disc_file}" "{eng_file}"'
    if os.path.exists(ai_ans_file):
        orchestrator_args += f' "{ai_ans_file}"'
    subprocess.run(f'python skills/audit-orchestrator/scripts/orchestrate.py {orchestrator_args} > "{final_file}"', shell=True, cwd=base_dir)
    
    # Print beautiful summary
    if os.path.exists(final_file):
        import json
        with open(final_file, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
            
        print("\n" + "="*50)
        print(f" AUDIT COMPLETE: {final_data['site']}")
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
        if md_file:
            print(f" LLM Markdown View saved to: {md_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_audit.py <url>")
        sys.exit(1)
        
    target_url = sys.argv[1]
    
    if not target_url.startswith("http"):
        target_url = "https://" + target_url
        
    run_audit(target_url)
