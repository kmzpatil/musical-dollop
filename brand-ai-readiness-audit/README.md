# Brand AI-Readiness Audit Marketplace

This is an advanced Agent Skill Marketplace designed to comprehensively audit websites for AI discoverability and on-site engagement. It replaces surface-level SEO checks with mechanistic AI-readiness validations, ensuring that a brand is accurately indexed, properly synthesized, and favorably cited by generative AI engines.

## Core Architecture

- **Automated Report Generation:** A unified runner script (`run_audit.py`) automatically executes the static analysis skills in sequence and stores the output in a structured `reports/<domain>/` directory.
- **Advanced Semantic HTML Parsing:** A centralized `parser.py` safely ingests raw HTML, extracting critical AI-readiness markers such as:
  - Heading hierarchies (`<h1>`)
  - Semantic content containers (`<main>`, `<article>`)
  - Accessibility metrics (Image `alt` text)
  - Duplicate content mitigation (Canonical tags)
  - OpenGraph / Rich preview social tags
  - Entity Disambiguation (`sameAs` in JSON-LD)
  - Schema-Type-Aware Completeness (Validates required fields like Product `offers`)
  - JS-Render Proxy Checks (detecting blank pre-render payloads)
- **Priority Scoring Engine:** The Orchestrator calculates a dynamic `Priority Score` based on an inverse-effort mathematical formula: `(Impact * 0.7) + ((6 - Effort) * 0.3)`. High-impact and low-effort tasks yield the highest priority score, which is then mapped to a normalized `Severity` level (Critical, High, Medium, Low) to create an actionable roadmap.
- **Mechanistic Action Snippets:** Suggested actions go beyond generic SEO advice by generating copy-pasteable code snippets (e.g., dynamically populated JSON-LD) and providing explicit, one-sentence mechanism justifications explaining *why* generative AI engines require the fix.
- **AI Crawler Directives:** Explicitly checks for AI bot blocks in `robots.txt` (e.g., `GPTBot`, `ClaudeBot`) and verifies the adoption of the emerging `llms.txt` standard.

## Skills Included

1. **audit-orchestrator** (Entrypoint): Collects the intermediate JSON outputs from all other modules and processes them through the Priority Scoring Engine to create the final unified report.
2. **discoverability-audit**: Analyzes the DOM for AI crawlability blockers. Checks for restrictive `robots.txt` (specifically for AI bots), the existence of `llms.txt`, JSON-LD structured data schema completeness (e.g. required `sameAs` or `offers` fields), canonical tags, OpenGraph meta properties, and flags images lacking `alt` attributes. Includes generated JSON-LD code snippets.
3. **engagement-audit**: Analyzes the site layout for semantic orientation. Enforces exactly one `<h1>`, requires `<nav>`/`<header>` landmarks, flags missing semantic content areas (`<main>`), tracks viewport readiness, and calculates maximum DOM depth to prevent crawler fatigue.
4. **ai-answerability-audit**: An agentic protocol (documented via `SKILL.md`) that performs a live self-test. It instructs an agent to extract factual claims from the site and diff them against live web-search LLM responses to test for factual degradation, hallucination, staleness, and lack of independent corroboration.

## Usage

You can run the static analysis pipeline locally using the automated wrapper script. 

```bash
python run_audit.py https://example.com
```

The system will create a structured directory at `reports/example.com/` containing:
- `discoverability.json` (Static Parsing)
- `engagement.json` (Static Parsing)
- `ai_answerability.json` (Generated separately via the Agentic Protocol)
- `final_report.json` (Combined Priority Score output)

### Example Final Report Output:
```json
{
  "site": "apple.com",
  "audited_at": "2026-09-03T01:31:39Z",
  "summary": { 
    "total_findings": 5,
    "critical": 1,
    "high": 1,
    "medium": 3,
    "low": 0
  },
  "findings": [ 
    {
      "id": "D-010",
      "title": "High JavaScript Dependency",
      "severity": "critical",
      "evidence": "Raw HTML body contains only 255 characters of text, but contains SPA container markers.",
      "impact": 5,
      "effort": 5,
      "suggested_action": {
        "summary": "Implement Server-Side Rendering (SSR) or dynamic rendering to serve populated HTML directly to AI crawlers. AI crawlers that don't execute JS will see a blank page, preventing indexing.",
        "priority": "critical"
      },
      "priority_score": 3.8
    }
  ]
}
```
