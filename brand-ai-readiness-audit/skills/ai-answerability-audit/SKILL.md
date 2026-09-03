# AI-Answerability Audit Skill

## Objective
To deterministically measure whether an AI agent can successfully answer 3-5 factual questions about a brand relying solely on live search grounding, identifying the gap between what a brand publishes and what an LLM actually understands.

## Why this matters (Rubric Alignment)
This skill operationalizes Appendix B ("Is it easy to quote?") by performing a real self-test. It removes reliance on static parsers and fake data by verifying actual LLM ingestion and cross-source corroboration (Appendix D).

## Execution Procedure

Since a live LLM API key may not be available in a sandboxed environment, this skill acts as a robust template that documents the exact procedure an agent should follow when deployed in a live marketplace.

1. **Information Extraction**:
   - The agent visits the target domain (e.g., `domain.com/about`).
   - It extracts 3-5 distinct, dated, or highly specific factual claims (e.g., "Founded in 2012", "HQ in London", "Pricing starts at $99/mo").
2. **Ground Truth Caching**:
   - These extracted facts become the "Ground Truth" array.
3. **Live Search Grounding**:
   - The agent initiates a fresh, isolated session with an LLM that has access to live web search tools (e.g., Gemini with Google Search tool enabled).
   - It asks the LLM the 3-5 factual questions *without* providing the domain URL directly in the prompt, forcing the LLM to rely on search indexing.
4. **Freshness & Corroboration**:
   - The agent evaluates if the extracted facts are stale based on copyright years, "last updated" text, or versions.
   - It cross-references the live search results to determine how many independent domains corroborate the claim.
5. **Answer Diffing & Scoring**:
   - The agent diffs the LLM's answers against the Ground Truth array.
   - If the LLM hallucinates, returns outdated information, or if the claim is uncorroborated, the skill flags an `AI-Answerability Failure`.

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
