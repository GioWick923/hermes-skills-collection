---
name: teach
description: Teach user a skill/concept over multiple sessions.
argument-hint: "What would you like to learn about?"
disable-model-invocation: true
---

# Teach

The user wants to learn something over multiple sessions. Treat the current directory as a **teaching workspace**.

## Workspace Structure

```
/mission/                 (or current dir)
├── MISSION.md            # Why they want to learn — grounds all teaching
├── REFERENCE/            # Compressed reference docs (cheat sheets, glossaries, syntax)
│   └── *.html
├── RESOURCES.md          # High-trust sources for knowledge acquisition
├── LEARNING-RECORDS/     # ADR-style records of non-obvious insights
│   └── 0001-<name>.md
├── LESSONS/              # Primary teaching unit — one self-contained HTML each
│   └── 0001-<name>.html
├── ASSETS/               # Reusable components (CSS, quiz widgets, simulators)
│   └── *
└── NOTES.md              # Scratchpad for user preferences
```

## Philosophy

**Knowledge** (from high-trust resources) → **Skills** (interactive lessons, retrieval practice) → **Wisdom** (real-world interaction, community)

- **Fluency** ≠ **Storage strength**. Build long-term retention via desirable difficulty: retrieval practice, spacing, interleaving.
- Never trust parametric knowledge. Use `RESOURCES.md` for primary sources.
- Lessons are **beautiful HTML** (Tufte-style), short, one tangible win, tied to mission, in zone of proximal development.
- Reuse assets — shared stylesheet first, then components.
- Mission drives everything. If unclear, ask first.
- Update `MISSION.md` and learning records when mission evolves.

## Lessons

- One self-contained HTML file per lesson at `./lessons/0001-<dash-case>.html`
- Open for user via CLI (`start`, `open`, `xdg-open`)
- Link to other lessons and reference docs via HTML anchors
- Cite primary sources
- Include reminder to ask followup questions

## Assets

- Reusable components in `./assets/` — CSS, quiz widgets, simulators, diagram helpers
- Reuse is default. Before authoring, read `./assets/` and build from existing.
- When new reusable component needed, write it in `./assets/` and link.

## Zone of Proximal Development

- Read learning records to gauge level
- Teach most relevant thing fitting their zone
- Challenge "just enough"

## Knowledge → Skills

- Knowledge first (low difficulty), then practice (effortful retrieval = storage strength)
- Interactive lessons: quizzes, real-world steps
- Tight feedback loops, immediate feedback
- Quizzes: same word/char count per answer, no formatting clues

## Wisdom

- Real-world testing → delegate to community (forum, subreddit, class, local group)
- Find high-reputation communities
- Respect user preference to not join

## Reference Documents

- Compressed essence of lessons, for quick reference
- Syntax, algorithms, glossaries, exercises, poses
- Glossaries are essential — once created, adhere in every lesson

## NOTES.md

- Record user teaching preferences, working notes
- Refer back when designing lessons