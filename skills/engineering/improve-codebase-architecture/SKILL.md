---
name: improve-codebase-architecture
description: Scan codebase for deepening opportunities, visual report.
disable-model-invocation: true
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. Aim: testability and AI-navigability.

## Process

### 1. Explore

**Scope before you scan — YAGNI.** Deepening pays off on recently changed code.

- If user named a module/subsystem/pain point → use it
- Otherwise: `git log --oneline` to find hot spots, explore those first
- Read `CONTEXT.md` and ADRs in the area first
- Explore organically, note friction:
  - Where understanding requires bouncing between many small modules?
  - Where modules are **shallow** (interface ≈ implementation)?
  - Where pure functions extracted for testability but bugs hide in calling (no **locality**)?
  - Where tightly-coupled modules leak across seams?
  - Which parts are untested/hard to test through current interface?
- Apply **deletion test**: would deleting concentrate complexity? "Yes" = signal.

### 2. Present as HTML Report

Write self-contained HTML to OS temp dir: `<tmpdir>/architecture-review-<timestamp>.html`. Open for user (`start`/`open`/`xdg-open`).

**Stack**: Tailwind CDN + Mermaid CDN. Mix Mermaid (graph-shaped) with hand-built divs/SVG (editorial visuals).

**Each candidate card**:
- Files involved
- Problem (why friction)
- Solution (plain English)
- Benefits (locality, leverage, testability)
- Before/After diagram (side-by-side, custom)
- Recommendation strength: `Strong` (emerald), `Worth exploring` (amber), `Speculative` (slate)

**End with Top Recommendation**: which candidate first and why.

**Vocabulary**: Use `CONTEXT.md` for domain, `codebase-design` skill for architecture terms (module, interface, depth, seam, adapter, leverage, locality). If `CONTEXT.md` defines "Order", say "Order intake module" — not "FooBarHandler" or "Order service".

**ADR conflicts**: Only surface if friction warrants reopening. Mark clearly: "contradicts ADR-0007 — but worth reopening because…"

See `references/HTML-REPORT.md` for full scaffold, diagram patterns, styling.

**After writing**: ask "Which of these would you like to explore?"

### 3. Grilling Loop

Once user picks, run `grilling` skill to walk decision tree — constraints, dependencies, shape of deepened module, what sits behind seam, what tests survive.

Side effects inline via `domain-modeling`:
- New term not in `CONTEXT.md`? Add it.
- Sharpening fuzzy term? Update `CONTEXT.md` right there.
- User rejects with load-bearing reason? Offer ADR (only if hard to reverse, surprising without context, real trade-off).
- Want alternative interfaces? Run `codebase-design` with design-it-twice pattern.