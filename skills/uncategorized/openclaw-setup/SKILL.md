---
name: openclaw-setup
description: Configure OpenClaw to work with Hermes Agent.
---

# OpenClaw Setup for Hermes Agent

Use when you want to configure OpenClaw to work with Hermes Agent, either by migrating existing OpenClaw configuration or setting up a new OpenClaw instance that integrates with Hermes.

## Procedure

1. **Verify OpenClaw configuration exists**
   - Check for `~/.openclaw/` directory and `openclaw.json` file.
   - If missing, create a basic config using the Docker setup guide or by copying an example.

2. **Prepare Hermes for migration**
   - Ensure Hermes is updated: `hermes update`
   - Restart gateways if needed: `hermes gateway restart`

3. **Run migration preview**
   - Execute: `hermes claw migrate --preset full --dry-run`
   - Review the list of items that would be migrated, noting any conflicts.

4. **Resolve conflicts**
   - If there is a conflict in `model-config` (or other), decide whether to overwrite Hermes config or keep existing.
   - To overwrite, use the `--overwrite` flag.
   - To keep Hermes config, you can edit `~/.hermes/config.yaml` manually after migration.

5. **Execute migration**
   - Run: `hermes claw migrate --preset full --overwrite --yes`
   - (Omit `--yes` if you want interactive confirmation.)
   - Wait for completion and review the migration report.

6. **Verify migrated configuration**
   - Check that `~/.hermes/.env` contains messaging settings.
   - Check that `~/.hermes/config.yaml` contains model configuration (or verify it matches your preference).
   - Ensure migrated skills appear in `~/.hermes/skills/openclaw-imports/`.

7. **Test OpenClaw integration**
   - Start a new Hermes session to load migrated skills and config.
   - Use Hermes to open a webpage, e.g.:
     ```
     hermes browser exec "import asyncio; from browser_use import Agent; agent = Agent(task='Abrir https://example.com'); asyncio.run(agent.run())"
     ```
   - Alternatively, delegate to a browsing skill: `delegate_task(name='obscura-browser', prompt='Open https://example.com and take a screenshot')`.

8. **Optional: Clean up leftover OpenClaw directories**
   - After confirming everything works, run: `hermes claw cleanup` to rename OpenClaw directories to `.pre-migration/`.

## Pitfalls

- **Do not forget to restart gateways after a Hermes update** — otherwise the migration may run with mixed module states leading to unpredictable behavior.
- **Model configuration conflict** — the migration will refuse to overwrite an existing model config unless `--overwrite` is used. Decide beforehand whether you want to keep Hermes' model or adopt OpenClaw's.
- **Secrets are not migrated by default** — if you need API keys, add `--migrate-secrets` to the migration command and ensure they are present in `~/.openclaw/.env` or config.
- **Migration preview shows what would be imported** — always run with `--dry-run` first to avoid surprises.
- **After migration, start a new session** — imported skills and memory entries only take effect in new Hermes sessions.

## References

- See the official migration guide: `hermes claw migrate --help`
- For Docker-based OpenClaw setup, refer to `docs/guides/openclaw-docker-setup.md` in the Paperclip/OpenClaw repository.
- For troubleshooting migration issues, consult the Troubleshooting section in the migration guide.