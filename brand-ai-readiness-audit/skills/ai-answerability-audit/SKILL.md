---
name: ai-answerability-audit
description: Verifies whether core brand facts can be unambiguously extracted and cited by LLMs.
---

# AI-Answerability Audit Skill

## Objective
To deterministically measure whether an AI agent can successfully answer 3-5 factual questions about a brand relying solely on live search grounding, identifying the gap between what a brand publishes and what an LLM actually understands.

## Why this matters (Rubric Alignment)
This skill operationalizes Appendix B ("Is it easy to quote?") by performing a real self-test. It removes reliance on static parsers and fake data by verifying actual LLM ingestion and cross-source corroboration (Appendix D).

## Execution Procedure

When executing this skill, the agent must perform the semantic evaluation based purely on the structured payload provided by the ingestion engine.

1. **Information Ingestion**:
   - Read `extracted_content.json` from the domain's report directory (`reports/<domain>/extracted_content.json`).
2. **Semantic Evaluation**:
   - Evaluate whether the brand's primary identity, core value proposition, and offerings can be definitively summarized from this text alone without external knowledge.
3. **Finding Generation**:
   - If the identity and core offerings are missing, ambiguous, or buried deeply such that an LLM would struggle to confidently extract them without prior knowledge, document an `A-001` answerability finding in `ai_answerability.json` for the orchestrator to pick up.

## Output Schema Example

```json
{
  "id": "A-001",
  "title": "Uncorroborated / Stale Factual Claims (Pricing)",
  "severity": "high",
  "confidence": "high",
  "evidence": "Ground truth on pricing is '$99/mo' but is uncorroborated across independent domains. Live search grounding returned '$49/mo'. AI models are surfacing stale data from 2021.",
  "impact": 5,
  "effort": 2,
  "suggested_action": {
    "summary": "Update pricing pages with 'dateModified' Schema.org tags and push updates to primary knowledge bases (Wikidata, Crunchbase) to ensure independent corroboration.",
    "priority": "high"
  }
}
```
