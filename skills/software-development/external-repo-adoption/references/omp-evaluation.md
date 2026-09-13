# OMP (Oh My Pi) Evaluation

## Source
- URL: https://omp.sh/
- Repo: can1357/oh-my-pi
- Stars: 30,546 | Forks: 3,143
- License: MIT
- Created: 2025-12-31 | Last updated: 2026-09-11
- Language: TypeScript + Rust core (~80k lines)

## Overview
Coding agent with IDE wired in. Fork of Pi (badlogic/mario zechner). Adds batteries included.

### Key Features
- **60+ providers** · **31 built-in tools** · **14 LSP ops** · **28 DAP ops**
- **Time-traveling stream rules** — aborts mid-stream if model goes off-script, injects rule, retries
- **Advisor model** — second model supervises every turn, injects inline notes
- **Native debugger** — lldb, dlv, debugpy integrated for C/Go/Python debugging
- **`/collab`** — live session sharing via link + QR
- **Subagents** — isolated worktrees with schema-validated results
- **Persistent Python + Bun workers** — agent can call tools from within cells

### Installation
```bash
# macOS/Linux
curl -fsSL https://omp.sh/install | sh

# Windows (PowerShell)
irm https://omp.sh/install.ps1 | iex

# Bun (recommended)
bun install -g @oh-my-pi/pi-coding-agent

# Homebrew
brew install can1357/tap/omp
```

## Comparison with Hermes

| Feature | OMP | Hermes |
|---------|-----|--------|
| Coding agents | Single (OMP) | 6 (Claude, Codex, Cline, OpenCode, Pi, OpenHands) |
| Subagents | Yes (isolated worktrees) | Yes (via delegate_task) |
| Debugger | Native (lldb/dlv/debugpy) | No native debugger |
| Stream rules | Time-traveling abort + retry | No equivalent |
| Advisor model | Yes (second model watches) | No equivalent |
| Collaborative sessions | `/collab` with QR | No equivalent |
| LSP integration | 14 ops | Via MCP tools |
| Model coverage | 60+ providers | Multiple providers |

## Ecosystem
Active with 30k+ stars, daily releases. Extensions:
- Web UIs: omp-deck, omp-web, oh-my-pi-gui
- Desktop apps: omp-desktop, gooey-pi
- Integrations: Figma, Firecrawl, Neovim bridge
- Nix support: yuxqiu/omp-nix

## Decision: NOT adopt (as of 2026-09-10)

### Why not?
1. **Duplication** — Already have 6 coding agents; OMP is #7
2. **Complexity** — New stack (Rust + Bun) to maintain
3. **Niche features** — Stream rules/advisor are nice-to-have, not critical
4. **User preference** — User asked about criteria, not installation

### When to reconsider?
- If user wants single tool that does everything (replace multiple agents)
- If native debugger needed frequently (LLM-vs-code debugging)
- If stream-rules or advisor solve real problems experienced now

## Key Learnings
- OMP is from same lineage as Pi (badlogic)
- Active development, high star count indicates strong community
- Windows support exists (PowerShell installer)
- Rust core suggests performance focus
