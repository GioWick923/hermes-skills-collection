---
category: deepseek
name: deepseek-harness
description: Launch DeepSeek Harness (dsh) on Windows; configure local/alternative providers.
version: "0.2.0"
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [deepseek, harness, ai, agents, node]
---

# DeepSeek Harness (dsh) – Windows guide

> **Estado operable (2026-09-10):** dsh headless funciona con `z-ai/glm-5.3-flash` vía
> OpenRouter. Verificado con prompt real (`DSH_SMOKE_OK`). Usar la sección
> **⚡ Configuración operativa** de abajo, no el flujo legacy.

## ⚡ Configuración operativa (VERIFICADA 2026-09-10 — usar esta)

Binary: `$LOCALAPPDATA/hermes/node/dsh.cmd` (v0.1.0-rc.8).

```bash
export DSH_HOME="$HOME/.dsh"
dsh --profile headless --patch "C:/Users/<USER>/.dsh/ollama-overlay.yml" "tarea aquí"
```

Componentes en `~/.dsh/`:
- `.credentials.yaml` — `OPENROUTER_API_KEY: <key>` (credenciales file-backed)
- `ollama-overlay.yml` — patch overlay (nombre histórico) con el provider REAL: openrouter/glm-5.3-flash
- `settings.yaml` — providers: openrouter (default) + ollama + ornith + ablit

### ⚠️ Gotchas críticos aprendidos (NO repetir)

1. **La sección `llm-pi-ai:` de settings.yaml NO llega al runtime** (schema la resuelve
   bien en test aislado pero el adapter queda dormant → `NO_ADAPTER`). **Workaround
   verificado**: `--patch` con overlay que configure DIRECTO el entry `llm-pi-ai`
   (`config.providers`) y `agent-default-model`. Sin overlay = sin adapter.
2. **Formato PatchOptions es FLAT**: `{id, config}` directo, NO anidado bajo `patch:`
   (verificado en `vendor/include/lib/types/index.d.ts` del repo).
3. **`--patch` requiere path nativo Windows** (`C:/...`); MSYS (`/c/Users/...`) → node lo
   trata literal → `C:\c\Users\...` → ENOENT.
4. **Keys de OrcaRouter en Hermes .env MUERTAS** (10-sep, curl directo → `Invalid API key`).
   BAI pide depósito para glm. **OpenRouter sirve `z-ai/glm-5.3-flash` gratis (Parasail)**;
   también existe `z-ai/glm-5.3-flash:free`.
5. **Puerto 3080**: EADDRINUSE = instancia vieja → `netstat -ano | grep 3080` + taskkill.
6. **Credenciales**: dsh resuelve `apiKeyEnv` vía credentials service (`.credentials.yaml`),
   NO vía env del shell — exportar la var no basta.
7. **Perfil headless no acepta `-c/--cwd`**; hacer `cd` antes en la shell.
8. **`--dump-config` NO muestra la user patch layer** — no sirve para verificar overrides;
   verificar con error de runtime real (progresión: MISSING_CREDENTIAL → NO_ADAPTER → 401 → OK).
9. **homePatchPath = `$DSH_HOME/cordis.patch.yml`** (nivel HOME, aplica a todos los perfiles,
   va después del profile layer).

### Setup desde cero (si .dsh se pierde)
1. `.credentials.yaml` con `OPENROUTER_API_KEY: sk-or-...`
2. Overlay con 2 patches: `agent-default-model` + `llm-pi-ai` (config.providers completo)
3. Smoke: `dsh --profile headless --patch <overlay> "Respond exactly with: DSH_SMOKE_OK"`

### Fallback local (Ollama) y estado de modelos locales
- El overlay queda en `C:/Users/<USER>/.dsh/ollama-overlay.yml` (nombre histórico; contiene el provider cloud REAL). El fallback local es Ollama (`qwen14-agent` → reemplazado por `hf.co/mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-abliterated-i1-GGUF:IQ2_M`, :11434), declarado en settings.yaml pero no en el overlay — para operar local, cambiar el overlay a provider `ollama`.
- Antes de declarar un modelo local como fallback, VERIFICAR que está realmente vivo y cargado (`curl :11434/api/tags` para Ollama, `netstat` + `curl /v1/models` para llama.cpp) — el log viejo de un server muerto y settings que apuntan a un GGUF borrado dan la impresión falsa de que funciona.
- Al REEMPLAZAR un modelo local: descargar/verificar el nuevo y probarlo con un prompt real ANTES de borrar el viejo — nunca borrar el fallback vigente sin haber validado el reemplazo end-to-end.

---

## 📦 Legacy install/build (solo si se reinstala desde repo)

DeepSeek Harness (`dsh`) is an open‑source AI agent harness providing a **web UI** (`http://127.0.0.1:3080`) and a **CLI** (`dsh web`, `dsh <mode>`). The repository lives at https://github.com/deepseek-ai/deepseek-harness.

## 🔧 Prerequisites (Windows host)
- **Node ≥ 22** (you have v22.23.2).
- **pnpm ≥ 11** (`pnpm --version` → 11.22.0).
- **Git** for cloning.
- **PowerShell or Bash (git‑bash/MSYS)** for command execution.
- **Internet connectivity** for npm package downloads.

## 🛠️ Installation
```sh
# Clone the repo (you already have it)
cd "$HOME"
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness

# Install npm dependencies (pnpm will reuse the lockfile)
pnpm install
```
> **Note:** Linux‑only `landlock-run` binaries appear with warnings; they are ignored on Windows.

## 🔧 Provider configuration (Ollama, local models, gateways)
See **references/provider-config.md** for the verified `settings.yaml` / `llm-pi-ai` layout,
patch-overlay override syntax, error taxonomy (`MISSING_CREDENTIAL` vs `NO_ADAPTER`), and
the node schema pre-check that isolates bad config from bad runtime wiring.

## 📦 Build (required for the Node entry point)
```sh
# Build host‑side and client‑side bundles
pnpm run build   # ≈ 8 s on a typical Windows PC
```
When the build finishes you will see many `dist/assets/...` files and a final line `✓ built in Xs`.

## 🚀 Running the Web UI
Two common approaches:
1️⃣ **Quick‑run via npx** (no local build needed, uses a pre‑bundled binary):
```sh
npx @deepseek-ai/dsh web
```
If you see `"dsh" no se reconoce…` the binary is not in your PATH.
2️⃣ **Run the compiled entry point** (recommended after building):
```sh
node --import tsx apps/cli/src/bin.ts web
```
Both commands start the UI at `http://127.0.0.1:3080`. Open that address in a browser.

## 💻 CLI usage (post‑build)
```sh
# Start the UI (same as above)
node --import tsx apps/cli/src/bin.ts web

# Launch a specific agent profile
node --import tsx apps/cli/src/bin.ts agent <profile>

# Load a custom plugin
node --import tsx apps/cli/src/bin.ts plugin <path>
```
**Tip:** Only use `npx @deepseek-ai/dsh <mode>` if you installed the binary globally (`npm i -g @deepseek-ai/dsh`). Otherwise stick to the `node …` form.

## ⚠️ Common pitfalls & troubleshooting
| Symptom | Likely cause | Fix |
|--------|--------------|-----|
| `"dsh" no se reconoce…` | Binary not on PATH (common on fresh Windows) | Run via `node --import tsx …` or install globally with `npm i -g @deepseek-ai/dsh`. |
| Build hangs/fails | Missing `pnpm` or outdated Node version | Verify versions (`node --version` ≥ 22, `pnpm --version` ≥ 11) and re‑run `pnpm install`. |
| Port 3080 already in use | Another process (e.g., previous `dsh`) occupies the port | Kill the process (`taskkill /PID <pid>`) or run on a different port: `node … bin.ts web --port 3081`. |
| `node_modules/.bin` missing `dsh` | The repository does not expose a binary; use the Node entry point instead. |

## 📂 Project layout (relevant parts)
```
deepseek-harness/
├─ apps/cli/src/bin.ts          # entry point used with `node --import tsx`
├─ packages/...                 # library code for host/client
├─ node_modules/.bin/           # Linux‑only binaries (ignore on Windows)
├─ pnpm-lock.yaml               # lockfile
└─ scripts/…                    # optional helper scripts
```

## ✅ Verification checklist
- [ ] Node ≥ 22 installed.
- [ ] pnpm ≥ 11 installed.
- [ ] Repository cloned at `C:/Users/<USER>/deepseek-harness`.
- [ ] `pnpm install` completed without errors.
- [ ] `pnpm run build` succeeded.
- [ ] `node --import tsx apps/cli/src/bin.ts web` opens `http://127.0.0.1:3080`.

---
*Generated by Hermes Agent on $(date)*