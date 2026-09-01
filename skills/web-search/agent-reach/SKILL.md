---
name: agent-reach
description: Check 15+ internet platform status via Agent Reach MCP
category: web-search
trigger: Check which internet platforms are available for your agent
---

# Agent Reach MCP Integration

## Overview
Agent Reach gives AI agents read/search access to 13+ internet platforms. It's an installer + doctor + config tool — after install, agents call upstream tools directly.

## MCP Server
The MCP server exposes a `get_status` tool that reports which channels are installed and active.

### Available Channels
1. **GitHub** — repos and code (needs gh CLI)
2. **YouTube** — videos and transcripts (needs yt-dlp + node)
3. **V2EX** — nodes, topics, replies (public API ✅)
4. **RSS/Atom** — feed reading ✅
5. **Exa Search** — web semantic search (needs mcporter + Exa MCP)
6. **Jina Reader** — arbitrary web pages ✅
7. **Bilibili** — videos, subtitles, search (search works ✅)
8. **Twitter/X** — tweets (needs cookies)
9. **Reddit** — posts and comments (needs rdt-cli + cookies)
10. **Facebook** — posts, pages, groups (needs OpenCLI)
11. **Instagram** — users, pages, posts (needs OpenCLI)
12. **Xiaohongshu** — notes (needs cookies)
13. **Xiaoyuzhou** — podcast transcripts
14. **Xueqiu** — stocks and community
15. **LinkedIn** — professional social

## Usage in Hermes

### Check Status
```python
# Via MCP tool call
result = await mcp.call_tool("agent-reach", "get_status", {})
```

### Install/Configure Channels
```bash
# Install all channels
agent-reach install --channels=all

# Install specific channels
agent-reach install --channels=twitter,xiaohongshu,reddit

# Configure cookies for Twitter
agent-reach configure twitter-cookies "<Cookie-Editor header string>"

# Configure cookies for XHS
agent-reach configure xhs-cookies "<Cookie-Editor JSON>"

# Configure proxy for restricted networks
agent-reach configure proxy "http://user:pass@ip:port"

# Run doctor
agent-reach doctor
```

## Configuration
MCP server registered in `config.yaml`:
```yaml
mcp_servers:
  agent-reach:
    command: python
    args: ["-m", "agent_reach.integrations.mcp_server"]
    timeout: 120
    enabled: true
```

## Notes
- Agent Reach is a **glue layer** — only routes and calls, doesn't reimplement
- After installation, use upstream tools directly (twitter-cli, yt-dlp, mcporter, etc.)
- Cookie-based auth (Twitter, XHS): use Cookie-Editor export method only
- XHS login: Cookie-Editor browser export only (QR will hang)
- For servers: OpenCLI channels (Facebook, Instagram) require desktop Chrome