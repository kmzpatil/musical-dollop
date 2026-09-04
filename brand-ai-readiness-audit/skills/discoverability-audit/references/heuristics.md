# Heuristics Rationale

## JSON-LD @graph Unwrapping
Many modern CMS platforms emit JSON-LD wrapped inside a `@graph` array. The discoverability parser explicitly unwraps these arrays because strict root-level type validation would otherwise generate false negatives for critical schemas like `Organization` or `Product`.

## SSR vs Client-Side Hydration
The parser evaluates the raw HTML payload directly rather than executing JavaScript. If the raw HTML body length is exceedingly small but contains a mount point (like `<div id="root">`), we flag it. AI engines (like GPTBot) operate on limited compute budgets and heavily prioritize statically resolvable DOMs over SPAs requiring a headless browser to hydrate.
