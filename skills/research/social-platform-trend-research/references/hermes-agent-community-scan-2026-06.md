# Hermes Agent community scan — June 2026

Session-specific reference captured from a Spanish user request asking for Reddit/X/Twitter/community signals about Hermes Agent skills/tools that are trending or useful.

## Access notes

- Reddit modern JSON/API returned HTTP 403 in this session.
- `old.reddit.com` public pages were accessible and useful.
- Browser automation failed because local Chrome was not installed; do not encode this as a durable limitation.
- X/Twitter direct search was not verifiably accessible without login. Treat X findings from search snippets or Reddit citations as indirect, not direct evidence.

## Useful source patterns

Reddit search patterns that worked or were useful:

- `https://old.reddit.com/search?q=%22Hermes%20Agent%22%20NousResearch&sort=new`
- `https://old.reddit.com/r/hermesagent/hot/`
- `https://old.reddit.com/r/hermesagent/new/`
- `https://old.reddit.com/r/nousresearch/search?q=Hermes%20Agent&restrict_sr=on&sort=new`
- `https://old.reddit.com/r/LocalLLaMA/search?q=Hermes%20Agent&restrict_sr=on&sort=new`

Search-engine fallback queries used:

- `"Hermes Agent" NousResearch reddit`
- `"hermes-agent" NousResearch reddit`
- `site:reddit.com "Hermes Agent" "Nous"`
- `"Hermes Agent" site:x.com NousResearch`
- `"hermes-agent" site:x.com NousResearch`
- `"Hermes Agent" "MCP"`
- `"Hermes Agent" "skills"`
- `"Hermes Agent" "gateway"`

Official cross-check sources:

- Hermes docs: `https://hermes-agent.nousresearch.com/docs`
- Kanban docs: `https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban`
- MCP docs: `https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp`
- Skills catalog: `https://hermes-agent.nousresearch.com/docs/reference/skills-catalog`
- GitHub releases: `https://github.com/NousResearch/hermes-agent/releases`

## Findings from accessible Reddit pages

`r/hermesagent` existed and described itself as an unofficial Hermes Agent community. Two high-signal posts surfaced:

1. **Kanban Setups Megathread — Hermes Agent (June 2026)**
   - Strong emphasis on built-in Kanban for durable multi-agent work.
   - Recommended starter: `orchestrator + worker`, not five profiles on day one.
   - `delegate_task` framed as better for short synchronous subtasks; Kanban for durable workflows.
   - Profile descriptions and `SOUL.md` matter for routing.
   - Common rosters: 2-profile starter, 3-profile standard, 5-profile fleet.
   - Cost warning: cloud API workers can burn cost quickly; use local/smaller models for high-volume workers.
   - Pitfalls mentioned: dispatcher not running, non-existent profile assignees, low `failure_limit`, workers missing task context, SQLite/index corruption reports in older versions.

2. **Building an orchestrator for Hermes Agent: Kanban, delegate_task, or a separate workflow layer?**
   - User proposed a coordinator that decomposes high-level goals into DAGs, assigns researcher/builder/browser/reviewer/synthesizer agents, tracks progress, and stores reusable lessons.
   - The best synthesis was: `delegate_task` for short work, Kanban for durable workflows, and an orchestrator profile/skill on top rather than a separate runtime unless Kanban cannot support the lifecycle.

## Official release/doc cross-checks

GitHub releases around v0.16/v0.17 supported these themes:

- Desktop app and dashboard/profile builder gained prominence.
- Background subagents were introduced/enhanced.
- Messaging reach expanded, including iMessage via Photon and official WhatsApp Business Cloud API adapter.
- Image generation learned editing.
- Skills Hub/browser and curator improved.
- MCP catalog/admin/webhook/memory surfaces became more visible in the dashboard.

## Recommended synthesis pattern for future answers

When a user asks what to implement in Hermes based on community chatter, prioritize:

1. Kanban simple base: `orchestrator + worker`.
2. Profiles + `SOUL.md` only as complexity demands.
3. `delegate_task` for short parallel subtasks.
4. MCP integrations only for tools the user truly uses.
5. Cron for recurring tasks/briefings/watchdogs.
6. Gateway messaging if the user wants mobile/remote operation.
7. Skills as reusable procedures after difficult tasks.
8. Curator/memory/session_search hygiene.
9. Model routing for cost control: strong model for planning/review, cheaper/local for repetitive workers.

## Non-obvious tips captured

- Do not use Kanban for everything; durable overhead is only worth it for long-running or multi-step workflows.
- The orchestrator should route and review, not implement.
- Start with two profiles; add specialists when context pollution or routing confusion actually appears.
- Profile descriptions are routing inputs, not documentation fluff.
- Limit concurrency for local/slow models to avoid timeouts and stale workers.
- Keep skills small and class-level; avoid one-off task narratives.
- Memory is for durable preferences/facts; use session search for task history.
- MCP tool sprawl can harm context and routing; install narrowly.
