# Image generation through the user's own ChatGPT / OpenAI account

Scope: making Hermes `image_gen` spend the user's own subscription/API quota instead of the
default FAL.ai backend.

## Default wiring (verified by inspecting live `.env` / `config.yaml`)
- `image_gen` toolset is listed under `platform_toolsets.cli`.
- Backend: **FAL.ai**, model **FLUX 2 Klein 9B**. Auth: `FAL_KEY` (`.env`,
  `# FAL.ai API Key - Image generation`).
- Debug toggle: `IMAGE_TOOLS_DEBUG=false` (`.env`).
- The `openai-codex` / `openai` LLM providers are **text only** — they do NOT generate images.

## Path A — ChatGPT web-session token (uses the Go/Plus image quota)
- Evidence the session is already wired: `auth.json` → `active_provider: openai-codex`,
  `auth_mode: chatgpt`, `base_url: https://chatgpt.com/backend-api/codex`.
- That token is a chatgpt.com **browser-session credential**, reusable in principle for the
  image endpoint `chatgpt.com/backend-api/...`.
- Pros: spends the user's existing subscription image quota; no extra API billing.
- Cons: endpoint is **undocumented / reverse-engineered**, changes without notice, OpenAI often
  adds anti-bot defenses (extra headers, proof-of-work), and automating with a web-session token
  may violate OpenAI ToS. Expect breakage. Requires writing a custom script/provider that reuses
  the same session token.
- Status in the originating session: investigated, NOT implemented/verified. Treat as experimental.

## Path B — OpenAI API key (stable, documented)
- Use `VOICE_TOOLS_OPENAI_KEY` (already referenced in `.env`) or a dedicated `OPENAI_API_KEY`.
- Point an image provider at `https://api.openai.com/v1/images`.
- Bills **API usage**, not the Go subscription. Native support — does not break.

## Decision rule
Offer Path A (flag instability) for "use my subscription"; keep Path B as the robust fallback.
Both need a one-time config change AND a real verification image generated before claiming done.
