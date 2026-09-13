---
name: audit-orchestrator
description: Coordinates the AI readiness audit and generates a prioritized report.
---

# Audit Orchestrator

This skill acts as the central coordinator for the Brand AI-Readiness Audit. It ingests the JSON output from various detection modules, normalizes the findings, applies a mathematical priority scoring engine, and generates an actionable final report.

## Execution Procedure

1. **Ingest Findings**: Read `discoverability.json`, `engagement.json`, and `ai_answerability.json` from the target domain's report directory.
2. **Apply Priority Scoring**: 
   For each finding, calculate the priority score using the inverse-effort formula:
   `Priority Score = (Impact * 0.7) + ((6 - Effort) * 0.3)`
3. **Normalize Severity**:
   Map the priority score to a readable severity tier:
   - Score >= 4.5: `critical`
   - Score >= 3.5: `high`
   - Score >= 2.5: `medium`
   - Score < 2.5: `low`
4. **Compile Report**: Group the findings, tally the severities for an executive summary, and write to `final_report.json`.

## Inputs
- Path to the domain's report directory containing the raw JSON finding arrays.

## Output Schema
```json
{
  "site": "example.com",
  "audited_at": "YYYY-MM-DDTHH:MM:SSZ",
  "summary": { "total_findings": 0, "critical": 0, "high": 0, "medium": 0, "low": 0 },
  "findings": [ ... sorted by priority_score descending ... ]
}
```
