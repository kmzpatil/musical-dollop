import sys
import os
import subprocess
from urllib.parse import urlparse

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
    
    print(f"[*] Audit complete! Final report saved to: {final_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_audit.py <url>")
        sys.exit(1)
        
    target_url = sys.argv[1]
    
    if not target_url.startswith("http"):
        target_url = "https://" + target_url
        
    run_audit(target_url)
