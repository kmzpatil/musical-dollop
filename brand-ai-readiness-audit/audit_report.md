# Brand AI-Readiness Audit — Comprehensive Code Review

> **Repository:** `musical-dollop/brand-ai-readiness-audit`
> **Audited:** 2026-09-04 · **Codebase:** 634 LOC across 4 Python files · **Dependencies:** Zero (stdlib only) · **Submission:** 28 KB

---

## 1. Executive Summary

### Verdict: **Competent Prototype with Critical Spec Gaps — 5.4/10**

| Category | Wt | Score | Wtd |
|:---|:---:|:---:|:---:|
| Spec Compliance (manifest, SKILL.md, output) | 25% | 5/10 | 1.25 |
| Off-Site Discoverability Detection | 20% | 6.5/10 | 1.30 |
| On-Site Engagement Detection | 20% | 4/10 | 0.80 |
| Architecture & Code Quality | 15% | 7/10 | 1.05 |
| Suggested Actions & Proactivity | 10% | 8/10 | 0.80 |
| AI-Answerability Skill | 10% | 2/10 | 0.20 |
| **Total** | **100%** | | **5.4/10** |

The architecture is honest — a shared HTML parser feeds two deterministic audit scripts, merged by an orchestrator with a priority-scoring engine. Zero third-party dependencies (28 KB zip) is a major strength. However, several spec-breaking defects would cause automated validators to reject the submission.

> [!IMPORTANT]
> **The single biggest risk:** `marketplace.json` is missing the `"entrypoint": true` field. A strict validator will reject the entire package. This is a 30-second fix.

---

## 2. Spec Compliance Matrix

### 2.1 `marketplace.json`

**File:** [marketplace.json](file:///home/dopleganger/Documents/Projects/Adobe_university/musical-dollop/brand-ai-readiness-audit/marketplace.json)

| Requirement | Status | Evidence |
|:---|:---:|:---|
| Valid JSON | ✅ | Parses without error; 4 skills declared |
| Has `name`, `version`, `description` | ✅ | All present at root level |
| Exactly ONE skill with `"entrypoint": true` | ❌ **FAIL** | **No skill object contains an `"entrypoint"` key.** The word appears only in a `description` string (L10), not as a boolean field. |
| All `path` fields resolve | ✅ | All 4 paths point to valid directories |

> [!CAUTION]
> **P0 Game-Breaker.** An automated pipeline checking `skills.filter(s => s.entrypoint === true).length === 1` returns `0`.

### 2.2 `SKILL.md` Files

| Skill | YAML Frontmatter | `name` | `description` | Steps | `scripts/` | `references/` |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| audit-orchestrator | ✅ | ✅ | ✅ | ✅ 4 | ✅ | ❌ |
| discoverability-audit | ✅ | ✅ | ✅ | ✅ 5 | ✅ | ❌ |
| engagement-audit | ✅ | ✅ | ✅ | ✅ 6 | ✅ | ❌ |
| ai-answerability-audit | ❌ **FAIL** | ❌ | ❌ | ✅ 5 | ❌ **None** | ❌ |

> [!WARNING]
> `ai-answerability-audit/SKILL.md` has **no `---` YAML frontmatter fences** — invalid per `agentskills.io`. Additionally, spec requires `name` to be lowercase-alphanumeric-hyphens; the other three skills use Title Case.

### 2.3 Output Schema

**Required:** `site`, `audited_at`, `summary` (`total_findings`, `critical`, `high`, `medium`), `findings[]` (`id`, `title`, `severity`, `evidence`, `suggested_action.summary`, `suggested_action.priority`)

| Issue | Detail |
|:---|:---|
| ⚠️ `summary.low` | Extra field not in required schema |
| ⚠️ `findings[].impact`, `effort`, `priority_score` | Extra fields leak into output |
| ⚠️ `findings[].confidence`, `suggested_action.snippet` | Inconsistent extra fields on some findings |
| ❌ Findings not sorted | SKILL.md promises *"sorted by priority_score descending"* — `orchestrate.py` never calls `.sort()` |

---

## 3. Off-Site Discoverability Detection

### 3.1 Robots.txt AI Crawler Check

**File:** [audit_discoverability.py:11-33](file:///home/dopleganger/Documents/Projects/Adobe_university/musical-dollop/brand-ai-readiness-audit/skills/discoverability-audit/scripts/audit_discoverability.py#L11-L33)

**Checks 6 bots:** `gptbot`, `claudebot`, `perplexitybot`, `oai-searchbot`, `ccbot`, `google-extended`

| Gap | Risk |
|:---|:---|
| Wildcard `User-agent: *` with `Disallow: /` not checked | **High FN** — sites blocking ALL bots appear clean |
| `Disallow: /private/` triggers finding even though homepage is accessible | **Medium FP** — any path-specific disallow fires the check |
| `Allow:` directives ignored | **Medium FN** — `Disallow: /` + `Allow: /public/` treated as total block |
| Multiple `User-agent` stacking | **Low** — only last `current_agent` tracked |
| `except Exception: return True, "No restrictive..."` | **High FN** — 403/500/timeout treated as "no restrictions" |

### 3.2 SSR / Client-Side Hydration

```python
if parser.body_text_length < 500 and (parser.has_root_div or parser.has_noscript):
```

**Assessment: Heuristic proxy, not a true SSR diff.** Only fetches raw HTML; no headless browser rendering. The 500-character threshold is arbitrary. Checks `id="root"` and `id="app"` but misses `id="svelte"`, `id="__next"`, etc. Short pages with `<noscript>` for accessibility will false-positive.

> [!NOTE]
> Acceptable trade-off for a hackathon (avoids Playwright dependency bloat), but should be acknowledged in SKILL.md.

### 3.3 JSON-LD Validation

**Strengths:** Parses real JSON (not regex), handles arrays, validates `Product.offers` and `Organization.sameAs`, generates **copy-pasteable JSON-LD snippets** with the actual page title.

| Gap | Impact |
|:---|:---|
| `@graph` arrays not unwrapped | False negatives on many real sites |
| Only `Product` and `Organization` types checked | Ignores `LocalBusiness`, `Article`, `FAQPage`, `WebSite`, `Person` |
| No `@context` validation | Accepts any JSON in `ld+json` tags |
| No `dateModified`/`datePublished` checks | Critical freshness signals missing |
| Silent `except: pass` on malformed JSON-LD | Bad JSON produces no finding |

### 3.4 OpenGraph — Dead Code

Parser counts `og:*` and `twitter:*` tags into `self.og_tags` ([parser.py:31,65-66](file:///home/dopleganger/Documents/Projects/Adobe_university/musical-dollop/brand-ai-readiness-audit/skills/shared/parser.py#L31)), but **no audit script ever reads this value**. Sites missing OpenGraph tags are never flagged. README claims this capability exists.

---

## 4. On-Site Engagement Detection

**File:** [audit_engagement.py](file:///home/dopleganger/Documents/Projects/Adobe_university/musical-dollop/brand-ai-readiness-audit/skills/engagement-audit/scripts/audit_engagement.py)

### What's Implemented

| Check | ID | Assessment |
|:---|:---:|:---|
| Orientation (nav/header) | `E-001` | ✅ Sound — both must be absent to fire |
| Dead-end detection | `E-002` | ⚠️ Counts ALL `<a>` links (including footer/external); no internal vs. external distinction |
| Mobile viewport | `E-003` | ✅ Sound |
| DOM depth >20 | `E-004` | ⚠️ Threshold arbitrary; values inflated by parser void-element bug (see §5) |
| Semantic containers | `E-005` | ✅ Sound |
| H1 count ≠ 1 | `E-006` | ✅ Sound — fires for both 0 and >1 |

### What's Critically Missing

> [!CAUTION]
> **Zero lines of code** check for modals, popups, cookie consent gates, interstitial ads, or blocking overlays. A grep for `popup|modal|overlay|cookie|interstitial|banner` returns **no results**. This is a core spec requirement.

Also absent: hero value-prop clarity analysis, context retention (breadcrumbs), CTA usability evaluation, and `BreadcrumbList` JSON-LD detection.

---

## 5. Architecture & Code Quality

### 5.1 Skill Decomposition — Genuine

Each skill maps to a distinct audit domain. The shared `parser.py` correctly centralizes HTML ingestion. The `ai-answerability-audit` is the outlier — beautiful specification, zero executable code. The `reports/apple.com/ai_answerability.json` is hand-written sample data.

### 5.2 DOM Depth Bug (P1)

**File:** [parser.py:45-48,99-102](file:///home/dopleganger/Documents/Projects/Adobe_university/musical-dollop/brand-ai-readiness-audit/skills/shared/parser.py#L45-L48)

`handle_starttag` increments depth for ALL tags, but void elements (`<img>`, `<br>`, `<meta>`, `<link>`, `<input>`, `<hr>`) never trigger `handle_endtag`. Depth drifts upward monotonically. Apple.com's reported `max_dom_depth = 206` is almost certainly inflated.

### 5.3 Error Handling Summary

| Location | Handling | Risk |
|:---|:---|:---:|
| `parser.py` URL fetch | Retry + exponential backoff | ✅ Good |
| `parser.py` JSON-LD parse | `except: pass` | ❌ Silent |
| Robots.txt fetch error | Returns "no restrictions" | ❌ False negative |
| Orchestrator file load | `except: pass` | ❌ Findings vanish silently |
| `run_audit.py` subprocess | No `check=True`, exit codes ignored | ❌ Crashes produce empty JSON |

### 5.4 Shell Injection Risk

**File:** [run_audit.py:25](file:///home/dopleganger/Documents/Projects/Adobe_university/musical-dollop/brand-ai-readiness-audit/run_audit.py#L25)

```python
subprocess.run(f'python ...py "{url}" > "{disc_file}"', shell=True)
```

User-supplied `url` interpolated into a shell command. Fix: use `subprocess.run([...], stdout=open(...))`.

### 5.5 Performance

Both discoverability and engagement audits call `parse_url(url)` separately — **the page is fetched twice**. Total runtime: ~7-35s for a single page. Well under 5 minutes. Multi-page audits not supported.

### 5.6 Dependencies — Major Strength

Every import is stdlib. Zero `pip install`. No model weights. 28 KB submission.

---

## 6. Suggested Actions Quality

**Mechanistic justifications are strong:**
- *"AI hallucination often stems from entity confusion when sameAs links are missing."*
- *"Multiple H1s force the parser to guess the primary topic, increasing the risk of entity misattribution."*

**Copy-pasteable JSON-LD snippets** with the actual page title are a genuine value-add. Priority scoring formula `(Impact × 0.7) + ((6 − Effort) × 0.3)` is mathematically sound.

**Missing proactive suggestions:** `dateModified` tags, FAQ/HowTo schemas, `BreadcrumbList`, Wikidata entity pushes.

---

## 7. AI-Answerability — Vaporware

The SKILL.md describes an excellent concept (extract facts → query LLM → diff answers). But there is **no `scripts/` directory, no Python file, no executable**. The sample `ai_answerability.json` is hand-crafted. The runner doesn't invoke it — just checks `if os.path.exists()`. The fabricated Apple HQ example claim is factually dubious.

---

## 8. Refactoring Roadmap

### P0 — Game-Breakers (< 15 min total)

| # | Issue | Fix |
|:---|:---|:---|
| **P0-1** | Missing `"entrypoint": true` | Add to `audit-orchestrator` in `marketplace.json` |
| **P0-2** | Missing YAML frontmatter on ai-answerability | Add `---\nname: ai-answerability-audit\ndescription: ...\n---` |
| **P0-3** | Findings not sorted | Add `all_findings.sort(key=lambda f: f.get("priority_score", 0), reverse=True)` |
| **P0-4** | `__pycache__/` committed | Add `.gitignore` |
| **P0-5** | Shell injection in `run_audit.py` | Replace `shell=True` with list args |

```diff
  # P0-1: marketplace.json
  {
    "id": "audit-orchestrator",
    "name": "Audit Orchestrator",
    "path": "skills/audit-orchestrator",
+   "entrypoint": true,
    "description": "..."
  },
```

```diff
  # P0-2: ai-answerability-audit/SKILL.md
+ ---
+ name: ai-answerability-audit
+ description: Agentic self-test verifying LLM factual extraction via live search grounding.
+ ---
+
  # AI-Answerability Audit Skill
```

```diff
  # P0-3: orchestrate.py
+     all_findings.sort(key=lambda f: f.get("priority_score", 0), reverse=True)
      report = {
```

### P1 — Core Quality (2-4 hours)

| # | Issue |
|:---|:---|
| P1-1 | Robots.txt: check `User-agent: *` with `Disallow: /` |
| P1-2 | Robots.txt: return "inconclusive" on fetch error |
| P1-3 | Fix DOM depth for void elements |
| P1-4 | Wire up OpenGraph finding (`og_tags == 0`) |
| P1-5 | Handle JSON-LD `@graph` arrays |
| P1-6 | Add popup/modal/overlay detection |
| P1-7 | Cache parsed page between skills |
| P1-8 | Remove `summary.low` or verify spec allows it |
| P1-9 | Strip extra fields from output or nest under `metadata` |
| P1-10 | Log warnings instead of silent `except: pass` |

### P2 — Polish

| # | Issue |
|:---|:---|
| P2-1 | SKILL.md `name` fields → lowercase-hyphens |
| P2-2 | Add `references/` directories with spec links |
| P2-3 | Add `test_parser.py` with sample HTML |
| P2-4 | Add `.gitignore` |
| P2-5 | Create stub `extract_facts.py` for ai-answerability |
| P2-6 | Distinguish internal vs. external links in `E-002` |
| P2-7 | Check subprocess exit codes |
| P2-8 | Add `argparse` CLI |

---

## 9. Final Verdict

**Strengths:** Zero dependencies, genuine domain expertise, mechanistic justifications, copy-pasteable snippets, clean skill separation, sound priority scoring.

**Fatal Weaknesses:** Missing `"entrypoint": true`, invalid YAML frontmatter, ai-answerability is vaporware, no popup/modal detection, DOM depth bug, unsorted findings.

> This is a **solid 60% implementation** demonstrating genuine architectural thinking and domain knowledge, submitted under time pressure with critical last-mile gaps. The P0 fixes require <15 minutes. The P1 fixes require 2-4 hours. The codebase is **not** vibe-coded — the heuristics are mechanism-aware, the architecture is clean — but it **is** incomplete against the stated requirements.
