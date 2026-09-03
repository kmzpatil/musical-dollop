---
name: Discoverability Audit
description: Analyzes the DOM for AI crawlability blockers (robots.txt, llms.txt, JSON-LD schema completeness).
---

# Discoverability Audit

This skill evaluates a brand's technical infrastructure to ensure generative AI engines can crawl, parse, and confidently extract structured entities from the site.

## Execution Procedure

1. **Robots.txt AI Directives**: Check `/robots.txt` for `Disallow` rules targeting known AI bots (`GPTBot`, `ClaudeBot`, `PerplexityBot`).
2. **llms.txt Adoption**: Check for a `200 OK` at `/llms.txt`.
3. **JS-Render Proxy**: Analyze the text-to-markup ratio. If the raw HTML body has < 500 characters but contains SPA root markers (`<noscript>`, `<div id="root">`), flag for High JavaScript Dependency.
4. **Schema.org Completeness**: Parse `<script type="application/ld+json">`.
   - If missing entirely, generate a copy-pasteable snippet for an `Organization` schema.
   - If `Product` is found, validate the `offers` property exists.
   - If `Organization` is found, validate `sameAs` exists for entity disambiguation.
5. **Canonicalization & Accessibility**: Ensure `<link rel="canonical">` exists and tally images missing `alt` text.

## Mechanism Justification
Every finding must include a `suggested_action.summary` that mechanistically explains *why* the AI engine requires the fix (e.g. "AI hallucination often stems from entity confusion when sameAs links are missing.")
