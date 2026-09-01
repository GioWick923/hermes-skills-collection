---
category: research
name: social-platform-trend-research
description: "Use when researching what communities on Reddit, X/Twitter, forums, or niche groups are saying about a product, framework, tool, skill, or workflow, especially when the user wants trends, recommendations, and non-obvious tips in a fast-scan table."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, social-platforms, reddit, twitter, trend-analysis, communities]
    related_skills: [blogwatcher, hermes-agent]
---

# Social Platform Trend Research

## Overview

Use this skill to turn noisy community chatter into a compact decision aid: what people are discussing, which tools/workflows are gaining traction, what is actually verified, and what the user should implement next.

The core discipline is **source-tiered synthesis**. Social platforms are often partially blocked, indexed incompletely, or full of reposted claims. Separate verified direct evidence from search snippets, indirect citations, and official documentation. Never present inaccessible X/Twitter snippets or Reddit API failures as if they were direct reads.

For a concrete Hermes Agent community scan example, see `references/hermes-agent-community-scan-2026-06.md`.

## When to Use

Use when the user asks for:

- Reddit/X/Twitter/community sentiment around a tool, framework, model, product, or agent.
- "What skills/tools are popular?", "what are people recommending?", or "what should I implement?"
- Tables that rank trends, usefulness, difficulty, recommendation strength, or next steps.
- Practical tips that are not obvious from official docs.

Don't use for:

- Formal academic literature review — use paper/database skills instead.
- Brand monitoring that requires login-only dashboards or paid APIs unless credentials are available.
- Single-source summarization where the user provided one URL or document.

## Research Workflow

1. **Clarify the target only if needed.** If the user names the product/tool and platforms, proceed. Completion criterion: target terms, platforms, and output shape are known.

2. **Search direct community sources first.** Try platform-native or lightweight endpoints before general web search:
   - Reddit: `old.reddit.com/search`, subreddit search, post pages, comment pages.
   - X/Twitter: direct web/X search only if accessible; otherwise use indexed search results and label them as indirect.
   - Forums/Discord-like public pages: official community pages, GitHub discussions, issue trackers, release comments.
   Completion criterion: at least 2-3 source classes attempted or the access limitations are explicitly known.

3. **Use fallback search without overstating it.** If APIs block or modern pages require login, query search engines for exact phrases, product names, repo names, author handles, and feature terms. Completion criterion: each claim is tagged mentally as direct, indirect, or official-reference-backed.

4. **Cross-check against authoritative docs/releases.** Community claims about features should be checked against official docs, changelogs, release notes, or repo pages when available. Completion criterion: recommendations do not rely solely on unverified social chatter when an official source exists.

5. **Extract patterns, not just mentions.** Group raw hits into trend classes: workflows, integrations, pain points, setup patterns, cost patterns, pitfalls, and emerging experiments. Completion criterion: every row in the final table has a clear actionable category.

6. **Rank for the user's implementation context.** For each trend, decide whether to implement now, later, watch, or skip. Consider difficulty, maintenance burden, cost, evidence strength, and overlap with what the user already has. Completion criterion: the final answer has opinionated priorities, not a neutral dump.

7. **Report access limits honestly.** If Reddit API 403s, X blocks unauthenticated access, or a browser is unavailable, state that briefly and use the best accessible alternatives. Completion criterion: no unsupported claim is phrased as direct platform evidence.

## Output Pattern

For Spanish-speaking users, default to practical Spanish unless they request otherwise.

Recommended structure:

1. **Resumen rápido** — 5-10 bullets of the strongest findings.
2. **Fuentes consultadas** — table with source, what was accessible, and evidence strength.
3. **Trend/recommendation table** — columns like:
   - Tendencia / herramienta
   - Qué facilita
   - Señal encontrada
   - Cómo implementarlo
   - Recomendación
4. **Top priorities** — numbered implementation sequence.
5. **Tips poco comentados** — compact, practical, and tied to real pitfalls.
6. **Caveats** — only when access limitations affect confidence.

## Evidence Labels

Use these internally and expose them when helpful:

| Label | Meaning | How to phrase |
|---|---|---|
| Direct | Read from a public post/comment/page | "Encontré en..." |
| Indirect | Search snippet, quote in another page, inaccessible original | "Señal indirecta / citado como..." |
| Official | Docs, releases, repo, changelog | "Confirmado por docs/releases..." |
| Inferred | Synthesis from multiple weaker signals | "Mi lectura es..." |

## Common Pitfalls

1. **Overclaiming X/Twitter.** X often blocks unauthenticated reads and search engines can be stale. If only snippets or secondary citations are accessible, say so.

2. **Treating API blocks as product facts.** A 403/blocked API is an access limitation, not evidence that there is no discussion.

3. **Counting mentions instead of usefulness.** Users usually need implementation guidance. Prioritize workflows and decisions over vanity popularity.

4. **Mixing official features with community desires.** Keep "people want this" separate from "the tool supports this".

5. **Creating a long flat list.** Collapse similar chatter into class-level rows like "Kanban orchestration", "profile specialization", "MCP integrations", or "cost routing".

6. **Reddit `.json` API often 403s or returns an HTML error body.** When `old.reddit.com/search.json` or `/r/SUB/hot/.json` yields empty/HTML (not JSON), fall back to scraping the HTML page directly with a browser-like User-Agent. Working recipe:
   `curl -s -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' 'https://old.reddit.com/r/SUB/hot/'`
   then extract post links/title with regex on the rendered HTML:
   `<p class="title"><a class="title may-blank[^"]*"[^>]*href="(/r/SUB/comments/[^"]+)"[^>]*>([^<]+)</a>`.
   The HTML pages (hot/new/top) return HTTP 200 even when the JSON API is blocked. Read comments by downloading the post HTML page and pulling `<div class="usertext-body">` blocks.

7. **Don't trust `/tmp` to persist between `terminal` calls on Windows/MSYS.** Write scratch files under `$HOME` (e.g. `$HOME/hermes_scan/`) — `/tmp` resets between separate terminal invocations in this environment.
6. **Reddit JSON API is often blocked.** On several hosts `old.reddit.com/search.json` and `/r/<sub>/hot/.json` return HTTP 403 or an empty HTML error body (not JSON), so `json.loads` raises `Expecting value`. Fall back to the **old.reddit HTML pages** (`https://old.reddit.com/r/<sub>/hot/`), which return 200. Parse post links with regex: `<p class="title"><a class="title may-blank[^"]*"[^>]*href="(/r/<sub>/comments/[^"]+)"[^>]*>([^<]+)</a>`. Then fetch each post HTML and extract `<div class="usertext-body[^>]*>(.*?)</div>` for body + comments. Working recipe in `references/reddit-old-reddit-html-access.md`. Also: write scratch/verify scripts under `$HOME`, NOT `/tmp` — on MSYS/Windows hosts `/tmp` does not persist between separate `terminal` calls.

## Verification Checklist

- [ ] Direct sources were attempted before relying on snippets.
- [ ] Blocked/inaccessible platforms are disclosed briefly.
- [ ] Official docs/releases were used to verify feature claims when available.
- [ ] Final table distinguishes evidence strength or at least avoids overclaiming.
- [ ] Recommendations are prioritized and practical.
- [ ] Non-obvious tips are extracted as reusable patterns, not one-off anecdotes.
