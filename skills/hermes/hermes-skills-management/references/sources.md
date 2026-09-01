# Hermes Skill Sources — verified July 2026

## Official
- Skills Hub: https://hermes-agent.nousresearch.com/docs/skills/ (95 built-in skills, 20+ categories)
- Skills system: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/
- MCP features: https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp
- Use MCP guide: https://hermes-agent.nousresearch.com/docs/guides/use-mcp-with-hermes

## Community repos (SKILL.md format, installable)
- Undermybelt/hermes-skills — https://github.com/Undermybelt/hermes-skills
  - 1422 published SKILL.md + routing artifacts
  - Categories: red-teaming/ 757, community/ 494, software-development/ 65,
    aegis/ 22, research/ 18, devops/ 17 (incl MCP), autonomous-ai-agents/ 5,
    creative/ 8, productivity/ 6, apple/ 5, github/ 5, mlops/ 5, + 15 others
  - Has `scripts/validate_skills.py` (safety validator) and `scripts/sync_publishable_from_runtime.py`
  - Install pattern: `rsync -a skills/<cat>/<skill>/ ~/.hermes/skills/<cat>/<skill>/`
- itgoyo/hermes-skills — https://github.com/itgoyo/hermes-skills
  - 310+ skills (MIT). Academic, Apple/macOS, marketing, design, finance, game dev, MLOps
  - Quick start: `git clone https://github.com/itgoyo/hermes-skills.git ~/.hermes/skills`

## Discovery / ranking hubs
- Agentskills.io — portable Hermes-format skills
- SkillHub — curated CN community
- 虾评 Xiaping — reviews/rankings/usage notes (CN)
- https://www.hermes-ai.net/skills/ — unofficial multi-language index (ES/中文/日本語/한국어/EN...)

## MCP quick reference (from official guide)
- Install extras: `cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"`
- Config block in config.yaml:
  ```yaml
  mcp_servers:
    project_fs:
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
  ```
- Filter tools per server with `tools: include: [...]` (minimize exposed surface).
- Reload: `/reload-mcp`. Verify: "which MCP-backed tools are available right now?"
- npm servers need Node + npx; Python servers use `uvx`.
