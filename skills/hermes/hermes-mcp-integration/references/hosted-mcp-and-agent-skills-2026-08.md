# Hosted MCP endpoints and external skill packs

Session note: when integrating recently discussed third-party capabilities, prefer hosted MCP endpoints when available and keep the local config simple.

## Working pattern

- Add hosted MCP servers directly by URL in Hermes config when the provider supports it.
- Verify the endpoint with a simple HTTP probe before trusting the integration.
- Treat external skill repos as packs of class-level workflows, not one-off hacks.

## Verified endpoints

- Context7 MCP: `https://mcp.context7.com/mcp`
- Browserbase / Stagehand MCP: `https://mcp.browserbase.com/mcp`

## Verification behavior observed

- A plain `HEAD`/unauthenticated request to the hosted MCP endpoints returns `400 Bad Request`, which is useful as a quick liveness check.
- Context7 also advertises auth metadata via `WWW-Authenticate` on the response, so the endpoint is alive even before client auth is completed.

## External skill pack pattern

- `addyosmani/agent-skills` is best treated as a reusable skill pack with broad lifecycle workflows.
- The repo contains 24 skills, so when adopting it, install the whole pack first and then prune or adapt later if needed.
- When integrating into Hermes, copying the repo's `skills/` directory into the Hermes skills root preserves the class-level layout.
