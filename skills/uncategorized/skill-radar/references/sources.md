# Source map

Use multiple source types because no single directory proves quality, momentum, or safety.

## Tier 1 — canonical and official

- OpenAI Skills catalog: `https://github.com/openai/skills`
- Anthropic Skills repository: `https://github.com/anthropics/skills`
- NVIDIA Skills catalog: `https://github.com/NVIDIA/skills`
- Vendor or project repositories explicitly linked by the Skill author

Use these for provenance, canonical files, compatibility, update history, and official status.

## Tier 2 — broad discovery

- Skills.sh: `https://skills.sh/`
- SkillsMD: `https://skillsmd.dev/`
- AgentSkills.to: `https://agentskills.to/`
- SkillHub: `https://www.skill-marketplace.com/`

Use directories to discover candidates and observe their native metrics. Do not compare unlike metrics as if they were equivalent. An install count, repository star count, page view, and directory rank measure different things.

## Tier 3 — direct repository search

Search GitHub for:

- Exact filename and format: `filename:SKILL.md`
- Topic combinations: `agent-skills`, `codex-skill`, `claude-skills`
- Recently updated repositories and new paths inside established repositories
- Releases, commits, issues, forks, contributors, license, and dependency files

Prefer the canonical repository over mirrors. Treat sudden star growth as a lead, not proof of usefulness.

## Tier 4 — weak-signal discovery

Use papers, newsletters, Reddit, Hacker News, X, blogs, and trend pages to discover:

- New problem categories.
- Repeated user complaints.
- Security incidents.
- Emerging build gaps.

Require stronger sources before asserting adoption, quality, provenance, or safety.

## Social heat

Use the official X API recent-search endpoint when an `X_BEARER_TOKEN` is configured. Search a seven-day window for the Skill name and canonical repository, request `public_metrics`, exclude reposts, and record post count, unique authors, likes, replies, reposts, and quotes. Treat X as a momentum signal only; do not infer functional quality or safety from engagement.

## Minimum evidence

For a shortlisted Skill, seek:

1. The canonical `SKILL.md`.
2. Repository history and license.
3. At least one adoption or demand signal.
4. Direct inspection of scripts and permissions.
5. A second independent source for claims about momentum.

If the canonical file cannot be inspected, cap confidence at 40 and do not recommend installation.
