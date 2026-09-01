---
name: handoff
description: Compile a durable handoff wiki (markdown + git) so the next agent resumes with a "where you left off" block.
argument-hint: "What will the next session focus on?"
disable-model-invocation: true
---

# Handoff → durable wiki (disciplina ai-memory)

> Adaptado de `akitaonrails/ai-memory`: memoria de largo plazo para agentes. En vez de un ticket volátil en TMPDIR, compilar a una **página markdown persistente + git** (tu vault Obsidian) que el siguiente agente puede leer y que tú puedes historialear con `git log`. Sin server nuevo, sin vector DB.

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

## Helper (genera la estructura automáticamente)

Usa `scripts/make_handoff.py` para crear el template con timestamp, frontmatter y bloque
"where you left off" ya armados; luego solo rellena las secciones:

```bash
python skills/productivity/handoff/scripts/make_handoff.py "OBJETIVO" \
  --project "F:/Modelos" --next-focus "continuar" --entities "merge,sdxl,vae,fp16"
```

Salida: `HANDOFF_CREATED <ruta-en-vault>` — copia esa ruta como base, rellena y verifica.
(El script ya imprime el bloque "where you left off"; rellena el resto dejado vacío.)

## DÓNDE guardar (cambio clave)

Guardar en **dos lugares**:
1. **Persistente (canónico, durable)** → en tu vault Obsidian:
   `~/Documents/Obsidian Vault/Memorias/Handoffs/handoff-<timestamp>.md`
   - El vault es git-versionado → puedes `git log`/`git diff`/restaurar (disciplina ai-memory).
   - Abres en Obsidian, `grep`-able, backup con `rsync`.
2. **Volátil (rápido, opcional)** → `$TMPDIR/handoff-<timestamp>.md` (o `%TEMP%`) como enlace.

> Usa el vault path de `OBSIDIAN_VAULT_PATH` (resolve primero; file tools no expanden vars).
> Fallback: `~/Documents/Obsidian Vault`.

## Include

1. **Objective** — what we were trying to achieve
2. **Current state** — what's done, what's blocked, what's next
3. **Key decisions** — any architectural/design choices made
4. **Files changed/created** — paths and brief purpose
5. **Suggested skills** — skills the next agent should invoke (from Hermes skill index)
6. **Context pointers** — reference existing artifacts by path/URL (specs, ADRs, issues, commits, diffs). Do NOT duplicate their content.
7. **Open questions** — anything unresolved the next agent should clarify

## Bloque "WHERE YOU LEFT OFF" (nuevo, estilo ai-memory)

Al inicio del doc, incluye un bloque `> 📍 Where you left off` que sea EL resumen de una línea
de continuidad — esto es lo que el siguiente agente inyecta como contexto al arrancar:

```markdown
> 📍 **Where you left off:** <1-2 frases: estado del objetivo + qué faltaba + siguiente paso concreto>
> Continuar desde: `handoff-<timestamp>.md` | Proyecto: `cwd` | Última acción: <verificada>
```

## Frontmatter con entidades (nuevo, para recall)

Para que el handoff sea encontrable después (FTS/grep/entidades), usa frontmatter con up to 10 nouns:

```yaml
---
type: handoff
created: <ISO timestamp>
project: <basename($cwd)>
next_focus: <user hint o "continue">
entities: ["<noun1>", "<noun2>"]
tags: [handoff, <project>]
source: "conversation"
---
```

> Esto reproduce el recall por entidades de ai-memory (exact/prefix match) sin coste de LLM.

## Redact

- API keys, passwords, tokens, PII
- Any secrets from `.env` or credential stores

## Tailoring

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the document accordingly.

## Conectar al flujo de memoria 3 capas (nuevo)

Tras escribir el handoff en el vault, **sincronizar** al sistema de memoria de 3 capas para que
sea recuperable sin grepear el vault:
1. **Capa 1 (vault)** → el archivo `.md` ya está (canónico).
2. **Capa 2 (gbrain)** → `gbrain import <vault>/Memorias/Handoffs` (o `put_page`) para que sea
   buscable semánticamente (si gbrain está sano).
3. **Capa 3 (memory)** → solo si hay un FACT durable (p.ej. "decisión X tomada"), guardarlo con
   `memory` categoría `decided`. NO guardar el log completo en memory (se infla).

## Output

- Archivo persistente: `~/Documents/Obsidian Vault/Memorias/Handoffs/handoff-<timestamp>.md`
- Archivo volátil opcional: `$TMPDIR/handoff-<timestamp>.md`
- Print the absolute path of the persistent file (y el bloque "where you left off").

## Example header

```markdown
> 📍 **Where you left off:** Merge SDXL a medias — base cargada, falta bake VAE + fp16. Siguiente: validar tensor count.

---
type: handoff
created: 2026-08-31T16:30:00-06:00
project: F:/Modelos
next_focus: continue
entities: ["merge", "sdxl", "vae", "fp16"]
tags: [handoff, merge]
source: "conversation"
---

# Handoff — <objective>
*Generated: <ISO timestamp> | Next focus: <user hint or "continue">*

## Objective
...

## Current State
- ✅ Done: ...
- 🔄 In progress: ...
- ⏳ Next: ...

## Key Decisions
- <decision>: <rationale>

## Files Touched
- `path/to/file` — <purpose>

## Suggested Skills for Next Agent
- `skill-name` — <why>

## Context Pointers
- `docs/adr/0003-xyz.md` — <relevance>
- PR #42 — <relevance>

## Open Questions
- <question>
```

## Verification

- [ ] File exists in vault (persistente) + readable (`read_file`)
- [ ] Frontmatter válido (type/created/entities/tags)
- [ ] Bloque "where you left off" presente al inicio
- [ ] Sin secretos (revisar)
- [ ] (opcional) `git log --oneline` en el vault muestra el commit del handoff
- [ ] (opcional) gbrain import/`search` lo recupera