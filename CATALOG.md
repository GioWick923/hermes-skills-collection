# 📚 Catálogo de Skills — Hermes Agent

**251 skills · 34 categorías** — colección curada y funcional.

| Categoría | # Skills |
|---|---|
| agency | 10 |
| agent | 1 |
| agent-skills | 24 |
| apple | 4 |
| automation | 1 |
| autonomous-ai-agents | 19 |
| communication | 4 |
| creative | 21 |
| data | 1 |
| data-science | 1 |
| deepseek | 1 |
| desktop | 1 |
| devops | 4 |
| devtools | 2 |
| email | 2 |
| engineering | 7 |
| github | 7 |
| hermes | 23 |
| infra | 1 |
| integrations | 4 |
| media | 6 |
| mlops | 27 |
| network | 2 |
| note-taking | 1 |
| performance | 1 |
| productivity | 26 |
| research | 16 |
| safety | 1 |
| security | 2 |
| smart-home | 1 |
| social-media | 1 |
| software-development | 23 |
| trading | 5 |
| web-search | 1 |

---

## 🗂️ agency

| Skill | Descripción |
|---|---|
| `agency-ai-engineer` | AI Engineer (Agency Agents → Hermes). Lleva ML/LLM a producción: desarrollo de modelos, RAG, fine-tuning, MLOps, inferencia en tiempo real/batch, y ética (bias, privacidad, interpretabilidad). Enfoque práctico y escalable. |
| `agency-architect` | Arquitecto de software (Agency Agents → Hermes). Diseña sistemas mantenibles y escalables con ADRs, DDD, patrones (hexagonal, modular monolith, microservicios, event-driven) y análisis de trade-offs. Prioriza dominio sobre tecnología. |
| `agency-backend-architect` | Backend Architect (Agency Agents → Hermes). Diseña backend escalable y seguro: esquemas de datos, APIs con contratos (OpenAPI/AsyncAPI/protobuf), confiabilidad (circuit breakers, idempotencia, DLQ) y observabilidad. Security-first y performance-conscious. |
| `agency-orchestrator` | Conductor multiagente de Agency Agents para Hermes. Orquesta un pipeline de desarrollo completo: arquitecto → [dev ↔ QA en bucle] → reality-checker. Usa subagentes Hermes (delegate_task) y gates de calidad con evidencias reales, no afirmaciones. |
| `agency-orchestrator` | Conductor multiagente de Agency Agents para Hermes. Orquesta un pipeline de desarrollo completo: arquitecto → [dev ↔ QA en bucle] → reality-checker. Usa subagentes Hermes (delegate_task) y gates de calidad con evidencias reales, no afirmaciones. |
| `agency-persona-conversion` | Procedimiento para convertir librerías de personas/agentes externas (p.ej. msitarzewski/agency-agents, MIT, ~147 agentes) en skills de Hermes: clonar, leer definiciones reales, destilar a SKILL.md con prefijo/ categoría, mapear 'spawn agent' a delegate_task, y verificar sin romper nada. |
| `agency-pipeline-test` | Cómo ejecutar y verificar el orquestador multiagente Agency (agency-orchestrator) en un proyecto real pequeño, de extremo a extremo, con evidencia en disco. Usar cuando se quiera probar el equipo Agency o cualquier pipeline de delegate_task. |
| `agency-reality-checker` | Reality Checker (Agency Agents → Hermes). Última línea de defensa contra aprobaciones de fantasía. Por defecto 'NEEDS WORK'; exige evidencia abrumadora (screenshots, tests, métricas reales) antes de certificar producción. Escéptico y basado en evidencia. |
| `agency-senior-developer` | Senior Developer (Agency Agents → Hermes). Implementador full-stack de calidad: escribe código limpio, performante y mantenible, aplica estándares premium y verifica cada elemento interactivo. No añade features no pedidas. |
| `agency-test-automation` | Test Automation Engineer (Agency Agents → Hermes). Construye suites E2E deterministas (Playwright/Cypress): selectores por rol, cero sleeps, datos aislados, CI paralelo con trazas, y anti-flake con root-cause. 'Un test flaky es un bug con tu nombre'. |

## 🗂️ agent

| Skill | Descripción |
|---|---|
| `agent-tentacles` | Map all tools/skills/MCP/CLIs before claiming any missing. |

## 🗂️ agent-skills

| Skill | Descripción |
|---|---|
| `api-and-interface-design` | Guides stable API and interface design. Use when designing APIs, module boundaries, or any public interface. Use when creating REST or GraphQL endpoints, defining type contracts between modules, or establishing boundaries between frontend and backend. |
| `browser-testing-with-devtools` | Tests in real browsers via Chrome DevTools MCP. Use when building or debugging anything that runs in a browser. Use when you need to inspect the DOM, capture console errors, analyze network requests, profile performance, or verify visual output with real runtime data. Requires the chrome-devtools MCP server to be configured. |
| `ci-cd-and-automation` | Automates CI/CD pipeline setup. Use when setting up or modifying build and deployment pipelines. Use when you need to automate quality gates, configure test runners in CI, or establish deployment strategies. |
| `code-review-and-quality` | Conducts multi-axis code review. Use before merging any change. Use when reviewing code written by yourself, another agent, or a human. Use when you need to assess code quality across multiple dimensions before it enters the main branch. |
| `code-simplification` | Simplifies code for clarity. Use when refactoring code for clarity without changing behavior. Use when code works but is harder to read, maintain, or extend than it should be. Use when reviewing code that has accumulated unnecessary complexity. |
| `context-engineering` | Optimizes agent context setup. Use when starting a new session, when agent output quality degrades, when switching between tasks, or when you need to configure rules files and context for a project. |
| `debugging-and-error-recovery` | Guides systematic root-cause debugging. Use when tests fail, builds break, behavior doesn't match expectations, or you encounter any unexpected error. Use when you need a systematic approach to finding and fixing the root cause rather than guessing. |
| `deprecation-and-migration` | Manages deprecation and migration. Use when removing old systems, APIs, or features. Use when migrating users from one implementation to another. Use when deciding whether to maintain or sunset existing code. |
| `documentation-and-adrs` | Records decisions and documentation. Use when making architectural decisions, changing public APIs, shipping features, or when you need to record context that future engineers and agents will need to understand the codebase. |
| `doubt-driven-development` | Subjects every non-trivial decision to a fresh-context adversarial review before it stands. Use when correctness matters more than speed, when working in unfamiliar code, when stakes are high (production, security-sensitive logic, irreversible operations), or any time a confident output would be cheaper to verify now than to debug later. |
| `frontend-ui-engineering` | Builds production-quality, accessible, responsive user-facing UIs. Use when building or modifying interfaces and pages, creating components, implementing layouts, meeting WCAG accessibility requirements, managing state, or when the output needs to look and feel production-quality rather than AI-generated. |
| `git-workflow-and-versioning` | Structures git workflow practices. Use when making any code change. Use when committing, branching, resolving conflicts, or when you need to organize work across multiple parallel streams. Use when cutting a release, choosing a semantic version bump, tagging, or writing a changelog. |
| `idea-refine` | Refines raw ideas into sharp, actionable concepts through structured divergent and convergent thinking. Use when an idea is still vague, when you need to stress-test assumptions before committing to a plan, or when you want to expand options before converging on one. Triggers on "ideate", "refine this idea", or "stress-test my plan". |
| `incremental-implementation` | Delivers changes incrementally. Use when implementing any feature or change that touches more than one file. Use when you're about to write a large amount of code at once, or when a task feels too big to land in one step. |
| `interview-me` | Extracts what the user actually wants instead of what they think they should want. Achieves this through one-question-at-a-time interview until ~95% confidence about the underlying intent. Use when an ask is underspecified ("build me X" without "for whom" or "why now"), when the user explicitly invokes ("interview me", "grill me", "are we sure?", "stress-test my thinking"), or when you catch yourself silently filling in ambiguous requirements before any plan, spec, or code exists. |
| `observability-and-instrumentation` | Instruments code so production behavior is visible and diagnosable. Use when adding logging, metrics, tracing, or alerting. Use when shipping any feature that runs in production and you need evidence it works. Use when production issues are reported but you can't tell what happened from the available data. |
| `performance-optimization` | Optimizes application performance across frontend, backend, queries, and databases. Use when performance requirements exist, when you suspect performance regressions, when Core Web Vitals or load times need improvement, when N+1 query patterns need fixing, or when profiling reveals bottlenecks. |
| `planning-and-task-breakdown` | Breaks work into ordered tasks. Use when you have a spec or clear requirements and need to break work into implementable tasks. Use when a task feels too large to start, when you need to estimate scope, or when parallel work is possible. |
| `security-and-hardening` | Hardens code against vulnerabilities. Use when handling user input, authentication, data storage, or external integrations. Use when building any feature that accepts untrusted data, manages user sessions, or interacts with third-party services. |
| `shipping-and-launch` | Prepares production launches. Use when preparing to deploy to production. Use when you need a pre-launch checklist, when setting up monitoring, when planning a staged rollout, or when you need a rollback strategy. |
| `source-driven-development` | Grounds every implementation decision in official documentation. Use when you want authoritative, source-cited code free from outdated patterns. Use when building with any framework or library where correctness matters. |
| `spec-driven-development` | Creates specs before coding. Use when starting a new project, feature, or significant change and no specification exists yet. Use when requirements are unclear, ambiguous, or only exist as a vague idea. |
| `test-driven-development` | Drives development with tests. Use when implementing any logic, fixing any bug, or changing any behavior. Use when you need to prove that code works, when a bug report arrives, or when you're about to modify existing functionality. |
| `using-agent-skills` | Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill that governs how all other skills are discovered and invoked. |

## 🗂️ apple

| Skill | Descripción |
|---|---|
| `apple-notes` | Manage Apple Notes via memo CLI: create, search, edit. |
| `apple-reminders` | Apple Reminders via remindctl: add, list, complete. |
| `findmy` | Track Apple devices/AirTags via FindMy.app on macOS. |
| `imessage` | Send and receive iMessages/SMS via the imsg CLI on macOS. |

## 🗂️ automation

| Skill | Descripción |
|---|---|
| `cron-content-delivery` | Deliver recurring daily/weekly content to the user via Hermes cron jobs — language-learning phrases, quotes, reminders, tips. Use when the user wants something sent on a schedule (especially to Telegram), with self-contained scripts, multiple fire times, date-seeded variety, and JSON history for spaced repetition. Covers the script-only (no_agent=true) cron pattern, Telegram-only delivery, the Windows path-duplication pitfall, and the clock-mock verification trap. |

## 🗂️ autonomous-ai-agents

| Skill | Descripción |
|---|---|
| `autonomy-engine` | Autonomous priority queue with time-profile scheduling. |
| `claude-code` | Delegate coding to Claude Code CLI (features, PRs). |
| `codex` | Delegate coding to OpenAI Codex CLI (features, PRs). |
| `computer-use` | Drive the desktop in the background without stealing focus. |
| `hermes-agent` | Configure, extend, or contribute to Hermes Agent. |
| `hermes-browser` | Use when the optional Hermes Browser companion plugin is installed and exposes cached Browser Context Protocol tools; check context availability first, then read or clear cached browser context safely. |
| `hermes-browser-extension` | Use when working with the Hermes Browser Extension for Chromium side-panel browser context, connection setup, troubleshooting, or Browser-to-Hermes workflows; use it to connect to local, Hermes Cloud, or remote gateways and to keep browser context handling safe and explicit. |
| `hermes-closed-loop-engineering` | Use when designing or executing non-trivial Hermes work as a closed feedback loop: verifiable goals, bounded iterations, independent verification, clean memory/skill updates, and evidence-backed completion. |
| `hermes-local-fallback` | Configure a LOCAL model server (Ollama, LM Studio, llama.cpp, vLLM) as an offline/cost-free FALLBACK for Hermes Agent, so it answers automatically when the primary online provider (OpenRouter/NVIDIA/etc.) is unreachable. Covers the fallback_providers mechanism, the OpenAI-compatible local endpoint, safe config.yaml editing (file tools are blocked for it), and real verification by simulating 'no internet' with a dead host. |
| `hermes-moa` | Configure, activate, and verify Mixture of Agents (MOA) in Hermes — the native virtual model provider that fans out to reference models and aggregates with one acting model. Covers the factory-preset gotcha, config.yaml editing (blocked for file tools), and end-to-end verification. |
| `local-ablit-delegation` | Use when restricted: delegate to local abliterated model. |
| `memory-consolidate` | Daily fact extraction with importance scoring and decay. |
| `merge-reconciler` | Neutral third-party resolution of agent merge conflicts. |
| `obscura-browser` | Use when Hermes needs fast scraping, JavaScript-rendered page extraction, browser automation, or MCP browser tools through the local Obscura Rust headless browser. |
| `opencode` | Delegate coding to OpenCode CLI (features, PR review). |
| `openhands-docker-setup` | Deploy and debug OpenHands (all-hands-ai) in Docker on Windows/MSYS. Covers the runtime-version-mismatch debugging chain (micromamba, conda env, network), runtime-image patching via Dockerfile overlay, LLM model selection for tool-calling agents (reasoning models like hy3 break OpenHands), and the OpenRouter free-tier daily-limit gotcha. Use when the user asks to set up, deploy, debug, or run OpenHands locally via Docker. |
| `pi-coding` | Use to delegate coding tasks to the Pi Agent CLI. |
| `self-reflect` | Generate-critique-correct loop using a cheap model. |
| `validate-output` | Hallucination detection and confidence scoring for results. |

## 🗂️ communication

| Skill | Descripción |
|---|---|
| `chat-closing-format` | Mandatory end-of-chat format for this user. Every chat must close with (1) recommended next steps, each option carrying a brief 'why', (2) a 0-100 'solidity / room-to-improve' battery with an icon, and (3) traffic-light (green/amber/red) warnings. Use at the end of EVERY turn that concludes a topic or the whole session. |
| `response-preferences` | Responde breve en español, con autonomía y emojis moderados. |
| `show-me` | Use when explaining code/architecture/flows to the user: show-me visual pattern. |
| `x-tweet-extract` | Extract X tweet text+image without login via syndication. |

## 🗂️ creative

| Skill | Descripción |
|---|---|
| `antvis-infographic` | Render professional infographics from AntV Infographic DSL using @antv/infographic (276 built-in templates). Use when the user wants a data/info graphic, visual summary, or infographic with real SVG output. |
| `architecture-diagram` | Dark-themed SVG architecture/cloud/infra diagrams as HTML. |
| `ascii-art` | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. |
| `ascii-video` | ASCII video: convert video/audio to colored ASCII MP4/GIF. |
| `baoyu-infographic` | Infographics: 21 layouts x 21 styles (信息图, 可视化). |
| `character-ref-sheet-krea` | Character reference sheet pipeline for Krea2. |
| `claude-design` | Design one-off HTML artifacts (landing, deck, prototype). |
| `comfyui` | Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for lifecycle and direct REST/WebSocket API for execution. |
| `comfyui-checkpoint-install` | Install a ComfyUI checkpoint; checks GPU fit, verifies run. |
| `design-md` | Author/validate/export Google's DESIGN.md token spec files. |
| `excalidraw` | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). |
| `humanizer` | Humanize text: strip AI-isms and add real voice. |
| `manim-video` | Manim CE animations: 3Blue1Brown math/algo videos. |
| `opentoonz` | Use when installing OpenToonz or generating .tnz projects. |
| `p5js` | p5.js sketches: gen art, shaders, interactive, 3D. |
| `popular-web-designs` | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. |
| `pretext` | Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HTML demos by default. |
| `sketch` | Throwaway HTML mockups: 2-3 design variants to compare. |
| `songwriting-and-ai-music` | Songwriting craft and Suno AI music prompts. |
| `stable-diffusion-setup` | Install/tune ComfyUI & Forge Neo on Windows RTX 3060. Autonomous image generation, model merging, and user operational style. |
| `touchdesigner-mcp` | Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 native tools. |

## 🗂️ data

| Skill | Descripción |
|---|---|
| `langextract-structured` | Extract structured information from unstructured text using Google LangExtract with precise source grounding and interactive HTML visualization. Use when the user wants to pull entities/fields from documents, notes, reports, or transcripts (e.g. 'extract medications from this note', 'pull key facts from this text', 'structure this report'). |

## 🗂️ data-science

| Skill | Descripción |
|---|---|
| `jupyter-live-kernel` | Iterative Python via live Jupyter kernel (hamelnb). |

## 🗂️ deepseek

| Skill | Descripción |
|---|---|
| `deepseek-harness` | Launch DeepSeek Harness (dsh) on Windows. |

## 🗂️ desktop

| Skill | Descripción |
|---|---|
| `local-terminal-pane` | Read the user's local terminal pane when Docker is down. |

## 🗂️ devops

| Skill | Descripción |
|---|---|
| `cloud-vps-setup` | VPS gratis: Oracle Free Tier, claves, OCI CLI, setup. |
| `free-cloud-vps` | VPS gratis (Oracle): cuenta, instancia, SSH, Docker. |
| `oci-cloud-vps` | Oracle Cloud VPS: free tier, API auth, VCN cleanup. |
| `sdlc-review` | Review Kanban handoffs and route verified outcomes. |

## 🗂️ devtools

| Skill | Descripción |
|---|---|
| `oauth` | Use when fixing OAuth redirect_uri errors on portless URLs. |
| `portless` | Use when using portless for named .localhost dev URLs. |

## 🗂️ email

| Skill | Descripción |
|---|---|
| `email-inbox-triage` | Triage an inbox: prioritize threads, draft replies safely. |
| `himalaya` | Himalaya CLI: IMAP/SMTP email from terminal. |

## 🗂️ engineering

| Skill | Descripción |
|---|---|
| `agent-api-gateway-patterns` | Cliente API con keys: allowlist, retries, sandbox con tope. |
| `codebase-design` | Shared vocabulary for designing deep modules. |
| `grill-with-docs` | Relentless interview creating docs (ADRs, glossary) inline. |
| `improve-codebase-architecture` | Scan codebase for deepening opportunities, visual report. |
| `resolving-merge-conflicts` | Resolve in-progress git merge/rebase conflict hunk by hunk. |
| `retro` | Use when reviewing a finished session to improve future runs: retro audit. |
| `web-console-iframe-automation` | Extraer IDs/datos de consolas SPA con contenido en iframes. |

## 🗂️ github

| Skill | Descripción |
|---|---|
| `codebase-inspection` | Inspect codebases w/ pygount: LOC, languages, ratios. |
| `github-auth` | GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login. |
| `github-code-review` | Review PRs: diffs, inline comments via gh or REST. |
| `github-issue-to-pr` | Carry a GitHub issue to a verified PR with honest CI state. |
| `github-issues` | Create, triage, label, assign GitHub issues via gh or REST. |
| `github-pr-workflow` | GitHub PR lifecycle: branch, commit, open, CI, merge. |
| `github-repo-management` | Clone/create/fork repos; manage remotes, releases. |

## 🗂️ hermes

| Skill | Descripción |
|---|---|
| `agent-red-team` | Red-team agent defenses via local uncensored model. |
| `bot-fleet-registry` | Audita la flota Hermes: skills, cronjobs y su salud. |
| `botdirectory-bridge` | Evalúa prompts de botdirectory.ai para portar a Hermes. |
| `headroom-integration` | Use Headroom proxy to compress tool outputs and save tokens. |
| `hermes-capability-enablement` | Enable Hermes Agent capabilities that ship disabled by default — native web_search (DDGS/Firecrawl/Tavily/etc.), speech-to-text / voice input (faster-whisper), voice mode, and other Tool Gateway features. Covers the correct venv, the config.yaml edit pattern (file-locked), and REAL verification. Use when the user says 'enable web search', 'turn on STT', 'add voice input', 'I don't have web_search', 'mejora tus herramientas', 'enable X capability', or asks to close a capability gap vs. the docs. |
| `hermes-config-versioning` | Version and back up Hermes Agent's own configuration (skills, profiles, SOUL.md, memories, cron, kanban) with git while excluding secrets/state — plus a safe tar backup for the parts git must never track. Use when the user wants to protect their Hermes setup, recover from a bad update, snapshot a multi-profile configuration, or 'back up my hermes config'. |
| `hermes-health-check` | Check Hermes with real commands before saying it is broken. |
| `hermes-mcp-integration` | Evaluate, install, and verify a third-party MCP server in Hermes Agent — npx/uvx/HTTP servers, config.yaml format, privacy flags, and the hermes mcp test verification loop. Use when the user asks to add/verify/recommend an MCP server (browser automation, filesystem, GitHub, databases, APIs) for Hermes. |
| `hermes-migration-restore` | Restore Hermes migration backup; fix cron/gbrain drift. |
| `hermes-multi-agent` | Configure and verify Hermes multi-agent capabilities: activate MOA (Mixture of Agents) virtual provider, create specialized profiles with SOUL.md personas, and wire delegation/Kanban. Includes the factory-preset dead-model gotcha and the config.yaml file-lock workaround. |
| `hermes-security-audit` | Audita configuración, skills, MCP y cron de Hermes. |
| `hermes-self-audit` | Set up and operate a zero-cost self-audit watchdog for the Hermes ecosystem (skills, profiles, cron, memory, state.db, second brain) via a no_agent cron + a bash health script. Use when the user wants Hermes to 'watch itself', 'audit itself', 'stay in order', 'self-monitor', or 'optimize/clean up the agent setup'. |
| `hermes-self-optimizing-loop` | Audits Hermes health and auto‑fixes common drifts. |
| `hermes-skill-install-verify` | Install, debug, and verify Hermes Agent skills from the hub/official/clawhub registries on Windows — platform-exclusion pitfalls, binary prerequisites, dangerous-verdict blocks, and ad-hoc verification discipline. |
| `hermes-skills-management` | Discover, evaluate, and install Hermes Agent skills (official hub, community repos, discovery hubs) and connect MCP servers — including the non-interactive install workaround required for automation/background runs. |
| `hermes-telegram-gateway` | Link Hermes Agent to Telegram end-to-end: create the bot, write TELEGRAM_BOT_TOKEN into ~/.hermes/.env, enable gateway.platforms.telegram in config.yaml, run the gateway, and — the critical gotcha — configure the user allowlist so the bot does not deny every message. Use when the user says 'vincular a telegram', 'link to telegram', 'conectar bot', 'telegram gateway', or asks how to talk to Hermes from Telegram. |
| `hub-skill-vetting` | Evaluate Hermes hub skills for safety, compatibility, and real usefulness BEFORE installing. Covers the resolver source-prefix quirk (install fails to match when display name has a space), the Windows 'platforms:' load-pitfall (skill installs but never appears in 'hermes skills list'), and a ToS/risk checklist for account- or broker-connected skills. Use whenever the user asks to install a hub skill, or before running 'hermes skills install <id>'. Pair with hermes-skill-install-verify for post-install checks. |
| `memory-hitrate` | Use when auditing or measuring Hermes memory quality. |
| `memory-layer-ops` | Store durable memory via the 3-layer memory bridge. |
| `neko-monitor-status` | Monitorea la salud del contenedor Neko Master. |
| `reply-closing-format` | Formato de cierre OBLIGATORIO al final de cada charla para este usuario. Cierra siempre con (1) recomendaciones de proximos pasos donde cada opcion lleva una breve explicacion del porqué, (2) un porcentaje de solidez/a-mejorar 0-100 como bateria con icono, y (3) semaforo para advertencias. No pidas confirmacion excesiva: propón y deja elegir. Usar SIEMPRE al terminar cualquier intercambio con este usuario. |
| `safe-autonomy-operations` | Opera autonomía segura con supervisión y límites duros. |
| `third-party-skill-install` | > |

## 🗂️ infra

| Skill | Descripción |
|---|---|
| `free-vps-provisioning` | VPS gratis Oracle: cuenta, instancia ARM, SSH, setup. |

## 🗂️ integrations

| Skill | Descripción |
|---|---|
| `ai-gateway-integration` | Integrate AI gateways: triage, deploy, wire, verify. |
| `chatgpt-web-bridge` | Bridge Hermes to the user's ChatGPT WEB account (chatgpt.com) to exercise capabilities Hermes lacks natively — e.g. image generation via the user's ChatGPT Go/Plus subscription. Covers extracting the session from saved page source, the requirements→sentinel→conversation call flow, why the local auth.json Bearer is insufficient, and the Obscura-browser fallback that needs no cookie extraction. Use when the user wants Hermes to "generate images / use my ChatGPT / drive my ChatGPT account / do X through my subscription". |
| `gbrain` | Set up and wire GBrain (garrytan/gbrain) — a Postgres/pgvector knowledge brain with hybrid RAG, a self-wiring typed knowledge graph, and an LLM synthesis layer — into Hermes as a persistent-memory MCP server. Use when the user wants agent memory / a 'second brain', meeting prep, a queryable Obsidian vault, or references garrytan/gbrain. Covers the Windows native-bun gotcha, the embedding_model init pitfall, and local Ollama embeddings. |
| `openai-compatible-api-testing` | Test OpenAI-compatible API gateways (custom base_url, key). |

## 🗂️ media

| Skill | Descripción |
|---|---|
| `gif-search` | Search/download GIFs from Tenor via curl + jq. |
| `heartmula` | HeartMuLa: Suno-like song generation from lyrics + tags. |
| `omniget-downloader` | Use when the user asks to download media or links. |
| `songsee` | Audio spectrograms/features (mel, chroma, MFCC) via CLI. |
| `tiktok-download` | Download a TikTok video when yt-dlp and Chrome cookies fail. |
| `youtube-content` | YouTube transcripts to summaries, threads, blogs. |

## 🗂️ mlops

| Skill | Descripción |
|---|---|
| `audiocraft-audio-generation` | AudioCraft: MusicGen text-to-music, AudioGen text-to-sound. |
| `civitai-article-publish` | Publish humanized articles/guides to Civitai for Gio. |
| `civitai-browser-publish` | Publish content to Civitai via logged-in browser. |
| `civitai-voice` | Voz de Gio + hooks/formato para guías y contenido. |
| `colibri` | Evaluate and integrate the JustVugg/colibri local inference engine for GLM-5.2 MoE on constrained hardware. |
| `dsh-ornith-bridge` | DSH usa Ornith local: proxy thinking off + settings pi-ai. |
| `env-policy` | Entornos Python: venv GPU/CPU, abrir-ejecutar-cerrar. |
| `evaluating-llms-harness` | lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.). |
| `granite-asr` | Transcribir audio a texto local con Granite Speech 5.0. |
| `huggingface-hub` | HuggingFace hf CLI: search/download/upload models, datasets. |
| `local-gguf-deployment` | Use when choosing GGUF quantizations for local VRAM. |
| `local-llm-constrained-output` | Delegar a Ollama con format=schema para JSON válido. |
| `local-llm-inference-optimization` | Use when tuning local LLM speed: llama.cpp flags, gotchas. |
| `local-llm-operator-loop` | Operar LLM local (Ornith/ablit) como backend: cerebro→manos. |
| `local-llm-picker` | Pick and recommend the right local LLM (GGUF quant, MoE, abliterated/uncensored) for the user's actual GPU/RAM, explain the concepts, and give runnable setup steps for llama.cpp / LM Studio on consumer hardware (incl. integrated GPUs). |
| `local-model-agent-integration` | Integra servidores locales OpenAI-compatibles con harnesses. |
| `local-model-harness-bridge` | Harness de agentes a modelos locales via proxy. |
| `local-model-install` | Inspect a HF model link, check fit, deploy to Ollama. |
| `local-ollama-vision` | Use when reading/OCR an image with the local Ollama VLM. |
| `local-tts-voice-cloning` | Use when running local TTS voice cloning on Windows CUDA. |
| `model-merge-publish` | Merge/publish Civitai checkpoints for Gio. |
| `model-router` | Elegir mejor modelo según la tarea (catálogo de gateways). |
| `openmythos-rdt` | Looped transformers/RDT (OpenMythos): MLA, MoE, ACT. |
| `rust-pyo3-accel` | >- |
| `sd-forge-fork-customization` | Prune, customize, and wrap a Stable Diffusion WebUI Forge / Forge-Neo fork (e.g. gi0baro/forge-neo) into a minimal personal build, and expose it headlessly so an agent (Hermes) can drive image generation without a browser. Use when the user wants a "mini" / "ligero" Forge with fewer models, a lighter UI, or agent-operated generation over an existing fork. |
| `sdxl-checkpoint-merging` | >- |
| `vram-watchdog` | Libera VRAM de modelos inactivos; recarga bajo demanda. |

## 🗂️ network

| Skill | Descripción |
|---|---|
| `darkweb-osint` | Buscar info via Tor cuando la web normal bloquea. |
| `wireguard-vpn` | Use for WireGuard VPN setup, double-hop, or iptables fix. |

## 🗂️ note-taking

| Skill | Descripción |
|---|---|
| `obsidian` | Read, search, create, and edit notes in the Obsidian vault. |

## 🗂️ performance

| Skill | Descripción |
|---|---|
| `python-hotpath-to-rust` | Acelera hot paths de Python en Rust SIN romper nada. Usar cuando un módulo Python de Hermes (o propio) tenga un cuello de botella aislable (loops sobre strings/listas, strip/trim, parsing, normalización, collapse de whitespace) y se quiera ganar velocidad compilando un .pyd con pyo3, manteniendo SIEMPRE fallback a Python puro y parity tests obligatorios. Aplica solo a funciones PURAS y pequeñas; NUNCA portar lógica de matching/difflib/mapeo de posiciones completa de golpe. El agente debe aplicar este flujo proactivamente en el futuro cada vez que detecte un hot path candidato en código Python que mantiene. |

## 🗂️ productivity

| Skill | Descripción |
|---|---|
| `airtable` | Airtable REST API via curl. Records CRUD, filters, upserts. |
| `box` | Box manages cloud files, sharing, search, and metadata. |
| `daily-focus-advisor` | Plan diario de enfoque: bloques realistas y qué aplazar. |
| `document-to-action-items` | Extract cited obligations, deadlines, tasks from documents. |
| `docx` | Create, read, edit Word .docx documents and templates. |
| `google-workspace` | Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python. |
| `gtm-obsidian-vault` | Setup GTM Obsidian vault with receipt notes. |
| `handoff` | Compile a durable handoff wiki (markdown + git) so the next agent resumes with a "where you left off" block. |
| `make-it-stick-study-lab` | Crea laboratorio de estudio de 7 días (Make It Stick). |
| `maps` | Geocode, POIs, routes, timezones via OpenStreetMap/OSRM. |
| `markitdown-convert` | Convert files to Markdown: PDF, DOCX, XLSX, PPTX, HTML, ZIP. |
| `meeting-action-items` | Turn meeting notes into cited decisions, owners, tickets. |
| `nano-pdf` | Edit PDF text/typos/titles via nano-pdf CLI (NL prompts). |
| `notion` | Notion API + ntn CLI: pages, databases, markdown, Workers. |
| `ocr-and-documents` | Extract text from PDFs/scans (pymupdf, marker-pdf). |
| `officecli` | Create, analyze, proofread, and modify Office documents (.docx, .xlsx, .pptx) using the officecli CLI tool. Use when the user wants to create, inspect, check formatting, find issues, add charts, or modify Office documents. |
| `pdf` | Create, merge, split, fill, and secure PDF files. |
| `petdex` | Install and select animated petdex mascots for Hermes. |
| `powerpoint` | Create, read, edit .pptx decks, slides, notes, templates. |
| `product-price-monitor` | Watch product, flight, or listing prices; alert on target. |
| `session-librarian` | Organize sessions by prompt: find, rename, archive, prune. |
| `teach` | Teach user a skill/concept over multiple sessions. |
| `teams-meeting-pipeline` | Operate the Teams meeting summary pipeline via Hermes CLI — summarize meetings, inspect pipeline status, replay jobs, manage Microsoft Graph subscriptions. |
| `torlink-downloader` | torlink HTTP API for torrent search, add, monitor. |
| `weekly-review-planning` | Weekly reset: commitments, stalled work, next-week plan. |
| `xlsx` | Create, read, edit Excel .xlsx spreadsheets and CSVs. |

## 🗂️ research

| Skill | Descripción |
|---|---|
| `arxiv` | Search arXiv papers by keyword, author, category, or ID. |
| `blocked-page-recovery` | Recover blocked/paywalled/WAF'd pages via fallbacks. |
| `blogwatcher` | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. |
| `competitor-news-monitor` | Watch named companies for material news; cited digests. |
| `deep-research-loop` | Multi-step autonomous research loop with role separation. |
| `grounded-citations` | Ground answers and documents in cited, verifiable sources. |
| `llm-wiki` | Karpathy's LLM Wiki: build/query interlinked markdown KB. |
| `markdown-browser` | Lightweight HTML-to-Markdown browser with viewport paging. |
| `polymarket` | Query Polymarket: markets, prices, orderbooks, history. |
| `read-x-tweet` | Leer tweets al instante sin auth (syndication): texto+media. |
| `research-paper-writing` | Write ML papers for NeurIPS/ICML/ICLR: design→submit. |
| `rqgm-coevolution-pattern` | Use when tuning LLM judges or self-eval loops: RQGM pattern. |
| `scrape-structured-json` | Scrape → markdown → JSON vía LLM local (format). |
| `social-platform-trend-research` | Use when researching what communities on Reddit, X/Twitter, forums, or niche groups are saying about a product, framework, tool, skill, or workflow, especially when the user wants trends, recommendations, and non-obvious tips in a fast-scan table. |
| `technical-comparative-research` | Compare hardware options with metrics, deliver visual docs. |
| `verdict-research` | Use when the user asks to research or investigate any topic. |

## 🗂️ safety

| Skill | Descripción |
|---|---|
| `safety-boundary-handling` | How to respond when a user asks to relax, override, or "just add a warning" to a hard safety/legality limit — distinguish non-overridable system candados from editable user preferences, explain origins honestly, and offer the legal alternative. |

## 🗂️ security

| Skill | Descripción |
|---|---|
| `1password` | Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in, and reading/injecting secrets for commands. |
| `supercookie-favicon-tracking` | Tracking via favicon/caché: Supercookie demo y defensa. |

## 🗂️ smart-home

| Skill | Descripción |
|---|---|
| `openhue` | Control Philips Hue lights, scenes, rooms via OpenHue CLI. |

## 🗂️ social-media

| Skill | Descripción |
|---|---|
| `xurl` | X/Twitter via xurl CLI: post, search, DM, media, v2 API. |

## 🗂️ software-development

| Skill | Descripción |
|---|---|
| `claude-code-free` | Run the Claude Code CLI for $0 using OpenRouter free models via a local Anthropic->OpenAI protocol proxy. Use when the user wants Claude Code without paying for Anthropic, or when wiring coding agents to free/open models. |
| `dogfood` | Exploratory QA of web apps: find bugs, evidence, reports. |
| `external-repo-adoption` | Adopt GitHub repos into Hermes: triage, port, verify. |
| `free-ai-coding-cli` | Run paid AI coding CLIs (Claude Code, Codex) for free by routing them to OpenRouter's Anthropic-compatible endpoint with a free model. Covers install, key setup, env-var redirection, and verification. |
| `free-claude-code` | Use when configuring the FCC free-model coding router. |
| `hermes-agent-skill-authoring` | Author in-repo SKILL.md: frontmatter, validator, structure, and writing-quality principles. |
| `hermes-model-config` | Manage Hermes Agent model/provider configuration — set default model, configure providers, handle fallbacks, and avoid common pitfalls. |
| `hermes-skill-integration` | Use when integrating a third-party community skill into Hermes from GitHub/ClawHub/skills.sh — install, repair incomplete snapshots, satisfy Python version gates, and verify it actually runs before declaring done. |
| `inspecting-hermes-desktop-dom` | Read the live Hermes desktop DOM/CSS over CDP. |
| `node-inspect-debugger` | Debug Node.js via --inspect + Chrome DevTools Protocol CLI. |
| `ornith-code-audit` | Codigo abliterado: Ornith genera, Hermes audita y refuerza. |
| `plan` | Plan mode: write an actionable markdown plan to .hermes/plans/, no execution. Bite-sized tasks, exact paths, complete code. |
| `provider-session-reuse` | Reuse Hermes' already-authenticated provider sessions (e.g. the ChatGPT web session behind the openai-codex provider) to power custom tool scripts, instead of provisioning a separate API key. Covers reading Hermes credential stores (auth.json is blocked by read_file but readable via terminal), the openai-codex token shape, the ChatGPT image-generation gotchas, and the honest verification discipline for reverse-engineered endpoints. |
| `python-debugpy` | Debug Python: pdb REPL + debugpy remote (DAP). |
| `python-version-provisioning` | Proyecto exige Python más nuevo que el host: usa uv run. |
| `requesting-code-review` | Pre-commit review: security scan, quality gates, auto-fix. |
| `rust-pyo3-python-accel` | Accelerate CPU-bound Python hot paths by porting them to Rust exposed via PyO3 + maturin. Covers candidate selection, the build workflow on Windows (MSVC linker shadowing pitfalls), UTF-8-correct string processing, and parity + benchmark verification. Use when the user wants to speed up Python code, especially repetitive/small hot paths in an agent, CLI, or tool. |
| `simplify-code` | Parallel 3-agent cleanup of recent code changes. |
| `spike` | Throwaway experiments to validate an idea before build. |
| `systematic-debugging` | 4-phase root cause debugging: understand bugs before fixing. |
| `test-driven-development` | TDD: enforce RED-GREEN-REFACTOR, tests before code. |
| `uv-run-helper` | Run a Python helper script whose dependencies are NOT in the active venv using uv. Covers the 'uv run' ephemeral-environment pitfall and MSYS/Windows path + python-vs-python3 conventions. |
| `windows-native-tooling` | Windows nativo en git-bash: rutas, codepage, taskkill. |

## 🗂️ trading

| Skill | Descripción |
|---|---|
| `alpha-orchestration` | Combine trading strategies via a 5-node signal graph. |
| `pine-script-indicators` | Use when working with TradingView Pine Script indicators. |
| `prediction-market-strategies` | Build Polymarket bots; strategies, fees, audit ledger. |
| `quant-research-cycle` | Ciclo hedge fund: idea, paper, backtest, veredicto. |
| `traderdev-mcp` | TraderDev MCP: auth verify + Pine backtest in Hermes. |

## 🗂️ web-search

| Skill | Descripción |
|---|---|
| `agent-reach` | Check 15+ internet platform status via Agent Reach MCP |
