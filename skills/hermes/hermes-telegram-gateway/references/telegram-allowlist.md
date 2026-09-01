# Telegram Allowlist — decision + how to get your user id

After `hermes gateway run` shows `Connecting to telegram...` and the bot connects,
it STILL rejects every inbound message unless an allowlist is configured:

```
WARNING gateway.run: No user allowlists configured. All unauthorized users will
be denied. Set GATEWAY_ALLOW_ALL_USERS=true in ~/.hermes/.env to allow open access,
or configure platform allowlists (e.g., TELEGRAM_ALLOWED_USERS=your_id).
```

## Option A — Open access (personal / single-user bot)
Add to `~/.hermes/.env`:
```
GATEWAY_ALLOW_ALL_USERS=true
```
Anyone who knows the bot's @username can talk to it. Acceptable when only the user
will use it. Restart the gateway after editing `.env`.

## Option B — Locked to you (recommended for shared/risky setups)
1. In Telegram, message **@userinfobot** (or **@getidsbot**). It replies with your
   numeric user id, e.g. `123456789`.
2. Add to `~/.hermes/.env`:
   ```
   TELEGRAM_ALLOWED_USERS=123456789
   ```
   Comma-separate multiple ids if needed. Restart the gateway.

## Getting the user id without a bot
@userinfobot and @getidsbot are the fastest. Alternatively, send a message to the
bot and read your sender id from `~/.hermes/logs/gateway.log` once it attempts
delivery (the log echoes sender metadata on denied attempts).

## Note
`.env` edits require the terminal+Python approach described in SKILL.md (the
agent write tools refuse to touch it). Make a backup first.
