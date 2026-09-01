# Caveman skill-pack analysis (JuliusBrussee/caveman)

Repo: https://github.com/JuliusBrussee/caveman — a "make your agent talk like a
caveman" skill-pack. ~30+ agent installers; ships 7 Hermes skills under
`skills/`. MIT, no telemetry post-install.

## What each skill does + stack-fit (user runs OpenRouter/Ollama, NOT Anthropic)

| Skill | Purpose | Fit on this stack |
|-------|---------|------------------|
| `caveman` | Persistent terse-speak mode (lite/full/ultra/wenyan). Prohibits emoji, decorative tables, pleasantries. | CONFLICTS with user's mandated ES + SIMPLE+DETALLADO + emoji + closing-format style. Install but keep OFF. |
| `caveman-commit` | Conventional Commit messages, <=50-char subject. Model produces text; no external API. | Useful. Works 100% offline. |
| `caveman-review` | One-line PR comments `L42: bug: user null. Add guard.` Model produces text. | Useful. Works 100% offline. |
| `caveman-compress` | Rewrites .md files to caveman prose, ~46% input-token saving. SHELLS OUT TO ANTHROPIC. | Needs ANTHROPIC_API_KEY+anthropic pkg OR `claude --print` CLI. Will fail or leak notes to Anthropic. Not usable as-is on OpenRouter/Ollama. |
| `caveman-stats` | Reads Claude Code session log for token savings. | Useless on Hermes (no Claude Code log). |
| `caveman-help` | Reference card of modes. | Minor. |
| `cavecrew` | Compressed subagents (OpenAI/Claude presets). | Not applicable to Hermes subagent model. |

## The critical finding (why caveman-compress is dangerous here)
`skills/caveman-compress/scripts/compress.py` -> `call_claude()`:
- Tries `anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])` with
  default model `claude-sonnet-4-5`.
- Falls back to `subprocess.run(["claude", "--print"], input=prompt)` — sends
  the file contents to the Anthropic API via the Claude Code CLI auth.
- `is_sensitive_path()` refuses obvious secret filenames, but the call itself
  is an external-data-boundary the user did not consent to.

User had: no ANTHROPIC_API_KEY, no anthropic pkg, but a `claude` binary on
PATH (Hermes' bundled node/claude). So a naive run would route notes to
Anthropic through that binary — violates the user's "no data without consent"
rule and their non-Anthropic stack.

## Install decision made (this session)
- Chose Option B: copy only caveman-commit, caveman-review, caveman-compress to
  %APPDATA%\hermes\skills\productivity\.
- Left caveman (style), caveman-stats, cavecrew, caveman-help out.
- Did NOT automate caveman-compress (would need Anthropic). Flagged to user;
  offered to patch compress.py to target Ollama gpt-oss:120b if they supply a
  real target .md + confirm Ollama is live when the cron fires.

## Installer safety notes
- `bin/install.js --only hermes` is benign: copies 7 dirs to
  ~/.hermes/skills/productivity/ (or HERMES_HOME), no post-install network,
  no config mutation. Requires Node >=18 (user had v22.23.1).
- It has a real uninstall path + dry-run (tested via tests/installer/hermes.test.mjs);
  earlier versions orphaned skill folders on uninstall (#524) — fixed in v1.9.1.
- Manual copy is preferred anyway: simpler to remove, no Node requirement.
