# Telegram delivery for cron jobs (Hermes)

## How delivery is chosen
`cronjob action=create` takes a `deliver` field:
- `telegram` → only the connected Telegram chat (HOME chat by default).
- `all` → every connected home channel (Telegram, Discord, etc.).
- `origin` / omitted → back into the originating session (NOT useful for fire-and-forget
  crons in the TUI, since the TUI has no live-delivery channel).
- `local` → saved only, nothing sent.

## Requirement
`deliver='telegram'` only works if the Telegram gateway is linked in Hermes. If the user
reports "no me llega nada", verify the gateway is connected before debugging the script.

## Gotchas
- In the TUI, a cron's stdout is saved but NOT delivered back into the chat. To actually
  notify the user, set `deliver` to a gateway channel (`telegram`/`all`).
- `no_agent=true` + empty stdout = silent (nothing sent). For content pushes you always
  want non-empty output.
- Multiple fire times require either a single `0 9,14,20 * * *` job (3 fires, same seed
  trick still yields differences only if you vary by hour) or 3 separate jobs.
