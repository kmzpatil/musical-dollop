import sys
import json
import datetime
from urllib.parse import urlparse

def calculate_priority_score(impact, effort):
    return (impact * 0.7) + ((6 - effort) * 0.3)

def determine_severity(score):
    if score >= 4.5:
        return "critical"
    elif score >= 3.5:
        return "high"
    elif score >= 2.5:
        return "medium"
    else:
        return "low"

def generate_report(url, files):
    all_findings = []
    
    for f_path in files:
        try:
            with open(f_path, 'r') as f:
                findings = json.load(f)
                all_findings.extend(findings)
        except Exception:
            pass

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for finding in all_findings:
        # If the finding has impact and effort, recalculate priority and severity
        if "impact" in finding and "effort" in finding:
            score = calculate_priority_score(finding["impact"], finding["effort"])
            finding["priority_score"] = round(score, 2)
            finding["severity"] = determine_severity(score)
            
            # Sync the suggested action priority with the orchestrator's computed severity
            if "suggested_action" in finding:
                finding["suggested_action"]["priority"] = finding["severity"]
            
        sev = finding.get("severity", "low").lower()
        if sev in severity_counts:
            severity_counts[sev] += 1

    parsed_url = urlparse(url)
    site = parsed_url.netloc if parsed_url.netloc else url

    report = {
        "site": site,
        "audited_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "total_findings": len(all_findings),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"],
            "low": severity_counts["low"]
        },
        "findings": all_findings
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python orchestrate.py <url> <result1.json> <result2.json> ...")
        sys.exit(1)
    
    url = sys.argv[1]
    result_files = sys.argv[2:]
    
    generate_report(url, result_files)
