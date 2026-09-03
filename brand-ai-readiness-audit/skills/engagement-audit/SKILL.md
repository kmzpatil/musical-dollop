---
name: Engagement Audit
description: Analyzes the site layout for semantic orientation (nav, headers, main) and internal linking.
---

# Engagement Audit

This skill evaluates a brand's HTML structure to ensure semantic clarity, proper navigation paths, and layout efficiency. AI models increasingly use these signals to determine page authority, readability, and user retention potential.

## Execution Procedure

1. **Orientation Check**: Verify the presence of `<nav>` or `<header>` elements. Without these, AI agents lack context on site taxonomy.
2. **Navigation Depth**: Count internal links and buttons. Too few links signal a "dead end," which harms authority scoring.
3. **Mobile Readiness**: Check for `<meta name="viewport">`. Mobile-responsive design is a universal requirement for positive indexing.
4. **DOM Complexity**: Measure maximum DOM depth. Flattened HTML structures reduce crawler fatigue and improve rendering speeds.
5. **Semantic Content Area**: Verify `<main>` or `<article>` tags exist. This helps LLMs isolate primary facts from advertorial noise.
6. **Heading Hierarchy**: Enforce exactly one `<h1>` tag to anchor the page's primary entity topic.

## Mechanism Justification
Every finding includes a `suggested_action.summary` explaining the mechanistic reason behind the failure (e.g. "Multiple H1s force the parser to guess the primary topic, increasing the risk of entity misattribution.")
