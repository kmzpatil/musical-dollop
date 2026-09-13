# Brand AI-Readiness Audit

## Problem Statement
In the evolving landscape of generative search and AI-driven discovery, a brand's visibility depends entirely on whether AI crawlers (like GPTBot, ClaudeBot, and PerplexityBot) can seamlessly read and extract its site content. 

However, enterprise Web Application Firewalls (WAFs) and bot-protection suites frequently intercept and block these automated user agents by default. Additionally, websites built heavily on Client-Side Rendering (CSR) or Single Page Applications (SPAs) act as "hydration traps"—serving empty HTML shells to crawlers that do not execute JavaScript. If generative engines are blocked by edge security or trapped by client-side rendering, they cannot confidently extract the brand's core facts, significantly degrading the brand's authority and recommendation frequency in AI-generated answers.

## Architecture Overview
This toolkit utilizes a highly efficient, two-stage execution pipeline designed for deterministic extraction and subsequent semantic evaluation:

### Stage 1 (Deterministic)
- Zero-dependency Python scripts handle the initial DOM parsing and data extraction.
- **WAF Detection:** Implements robust 403 bypass handling and signature detection to verify if edge security is actively blocking crawlers.
- **SPA Detection:** Identifies hydration shells and assesses text-to-markup ratios to warn against un-rendered DOM traps.
- Natively parses HTML elements, links, structural layouts, and JSON-LD schema using Python's built-in `html.parser`, generating a structured and sanitized payload without relying on heavy third-party web scraping libraries.

### Stage 2 (Semantic)
- The AI Agent receives the sanitized text payload (via `extracted_content.json`).
- Autonomously evaluates the semantic answerability of the brand's content.
- Measures how effectively the brand's identity and value propositions translate into reliable entity graphs for AI training weights and real-time indexes.

## Available Skills
This repository comprises four modules defined in the `agentskills.io` standard:

1. **`audit-orchestrator`**: Coordinates the AI readiness audit sequence and compiles the granular findings into a single, prioritized JSON report.
2. **`ai-answerability-audit`**: Verifies whether core brand facts and entities can be unambiguously extracted and confidently cited by LLMs.
3. **`discoverability-audit`**: Analyzes the DOM for AI crawlability blockers (robots.txt permissions, llms.txt adoption, JSON-LD schema completeness, and WAF intercepts).
4. **`engagement-audit`**: Evaluates the semantic orientation of the layout, structural depth, internal linking, and detects intrusive overlays that might trap bots.

## Setup & Execution

### Local Deployment
To deploy the skills locally for your agent environment, simply copy the `skills/` directory contents to your workspace's `.agents/skills/` directory:

```bash
cp -r skills/* .agents/skills/
```

### Execution
Once deployed, you can invoke the orchestrator via the Antigravity IDE chat by prompting the agent directly. For example:

> "@agent Run the audit-orchestrator on https://example.com"

## Key Features
- **Zero-Dependency Footprint**: Built entirely on standard library modules (`urllib`, `html.parser`), ensuring a lightweight footprint compliant with strict execution environments.
- **Strict Schema Compliance**: Enforces rigorous JSON output structures, guaranteeing programmatic aggregation and preventing unstructured output anomalies.
