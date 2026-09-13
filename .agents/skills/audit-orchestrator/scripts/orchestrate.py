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

        allowed_finding_keys = {"id", "title", "severity", "evidence", "suggested_action"}
        metadata = {}
        keys_to_move = [k for k in finding.keys() if k not in allowed_finding_keys]
        for k in keys_to_move:
            metadata[k] = finding.pop(k)
        if metadata:
            finding["metadata"] = metadata

        if "suggested_action" in finding:
            allowed_action_keys = {"summary", "priority"}
            action_metadata = {}
            action_keys_to_move = [k for k in finding["suggested_action"].keys() if k not in allowed_action_keys]
            for k in action_keys_to_move:
                action_metadata[k] = finding["suggested_action"].pop(k)
            if action_metadata:
                if "metadata" not in finding:
                    finding["metadata"] = {}
                finding["metadata"]["suggested_action_metadata"] = action_metadata

    parsed_url = urlparse(url)
    site = parsed_url.netloc if parsed_url.netloc else url

    all_findings.sort(key=lambda f: f.get("metadata", {}).get("priority_score", 0) if "metadata" in f else f.get("priority_score", 0), reverse=True)

    report = {
        "site": site,
        "audited_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "total_findings": len(all_findings),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"]
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
