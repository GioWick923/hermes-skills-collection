---
category: hermes
name: memory-layer-ops
description: "Store durable memory via the 3-layer memory bridge."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [memory, persistence, obsidian, gbrain, bridge, knowledge-management]
    related_skills: [headroom-integration, hermes-observational-memory, hermes-obsidian-ops]
---

# Memory Layer Ops — 3-Layer Memory Bridge

Class-level skill for operating Hermes' 3-layer persistent memory architecture.
Not tied to any single tool — covers the protocol, commands, and automation
for writing durable facts to the canonical layer (Obsidian), syncing to the
semantic index (gbrain), and reading context back.

## Architecture

```
┌───────────────────────────────────────────────────┐
│  Layer 1: OBSIDIAN VAULT (canónica, visible)      │
│  ├─ Memorias/Agente/*.md  — hechos persistentes   │
│  ├─ 10-Diario/*.md        — consolidación diaria   │
│  └─ 20-Proyectos/*.md     — contexto de proyectos  │
├───────────────────────────────────────────────────┤
│  Layer 2: GBRAIN MCP (índice semántico, embeds)   │
│  └─ sync vía bridge consolidate (cron 4am)         │
├───────────────────────────────────────────────────┤
│  Layer 3: HERMES MEMORY (built-in, short-term)    │
│  └─ facts entre sesiones, 2.2K chars               │
└───────────────────────────────────────────────────┘
```

## Bridge script

**Ruta:** `$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py`

| Comando | Función | Cuándo usarlo |
|---------|---------|---------------|
| `remember <text> --category X --tags Y` | Guarda hecho en Memorias/Agente/ | Al final de sesión/al aprender algo importante |
| `recall <query>` | Busca en vault + Hermes memory | Antes de responder con info durable |
| `consolidate` | diario con learnings del día | Fin de sesión (o cron 4am) |
| `health` | Check de estado del vault | Diagnóstico |
| `sync-gbrain` | Sincroniza notas a gbrain | Diario (cron 4am) |
| `process-inbox [--apply]` | Procesa capturas | Semanal |

## Protocolo para el agente

1. **Antes de responder con info durable**: ejecutar `recall <query>` — no asumir que la built-in memory es suficiente
2. **Después de aprender algo duradero**: ejecutar `remember` con frontmatter completo
3. **Al final de sesión**: ejecutar `consolidate` (el cron 4am lo hará si se olvida)
4. **Decisiones de arquitectura**: persistir con `--epistemic decision --confidence high`
5. **Contexto de usuario**: checkear memory built-in, luego vault (recall), luego web

## Frontmatter estándar

Notas en `Memorias/Agente/`:
```yaml
type: config|decision|learning|preference|fact
confidence: high|medium|low
epistemic: fact|self_report|observation|hypothesis|preference
tags: [tag1, tag2]
source: hermes
```

## Routing

| Tipo | Destino |
|------|---------|
| Config/decisiones/learnings/preferencias/facts | `Memorias/Agente/` |
| Consolidación diaria | `10-Diario/` |
| Capturas rápidas | `00-Inbox/` |
| Proyectos | `20-Proyectos/` |

## Cuando la memoria rápida (Layer 3) llega al 100%

La built-in memory se llena fácil (2.2K chars). La solución NO es borrar a ciegas:
**mover los detalles operativos al vault y dejar solo punteros en la memoria rápida.**

1. **Consolidar en el vault** una nota `reference` con todos los detalles que ya no
   caben (paths, comandos, configs, rutinas):
   ```bash
   python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" remember \
     "PUNTEROS OPERATIVOS: <detalle1>. <detalle2>. ..." --category reference --tags "operativo,consolidacion"
   ```
2. **Limpiar la memoria rápida** con un batch `memory` que elimina las entradas
   operativas redundantes (ya en vault/skills) y agrega la nueva, todo en UNA llamada
   `operations` (es atómico y chequea el límite solo al final).
3. **Dejar solo punteros** en la memoria rápida: quien eres + decisiones clave; el
   detalle técnico vive en vault (ilimitado) + skills.
4. **Regla de oro**: memoria rápida = índices; vault+gbrain = detalle. Así no se
   vuelve a llenar cada semana.

> El tool `memory` avisa si un batch excede el límite y pide consolidar en la MISMA
> llamada. Si dice "stop retrying" por exceso de reintentos en un turno, usar el vault
> (bridge) como destino canónico y dejarlo para otro turno — no es pérdida.

## Pitfalls

- **MSYS path**: en git-bash `/c/Users/...` → `C:\Users\...`. Preferir nativa.
- **No editar notas del agente** sin actualizar frontmatter.
- **gbrain sync** solo indexa notas nuevas por mtime. Editar no re-indexa.
- **No duplicar**: hecho va a Memorias/Agente/ o Inbox, no ambos.
- **Nunca sobrescribir** sin diff. `process-inbox` preview por defecto.

## Verificación

```bash
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" health
python "$LOCALAPPDATA/hermes/scripts/hermes_obsidian_bridge.py" recall "query de prueba"
```

## gbrain — Búsquedas semánticas

La bridge NO usa gbrain para recall (solo para sync). Para búsquedas semánticas:

```bash
# Verificar gbrain corriendo
tasklist | findstr bun

# Buscar con CLI directo
cd %USERPROFILE%\mcp-servers\gbrain-server
%USERPROFILE%\tools\bun.exe run src/cli.ts recall --query "modelo provider"

# Si sources.default está vacío, configurar:
gbrain config set sources.default obsidian-vault
```

### Troubleshooting común (2026-09-01)
- `gbrain sync` falla con "single-writer lock": Matar PID y reiniciar con `self-upgrade`
- Versiones distintas: `gbrain --version` vs `src/cli.ts` debe coincidir
- `sources.default` vacío: Causa principal de búsquedas que retornan 0 resultados

#### `sync-gbrain` → "Not inside a git repository: <vault>"
El vault ES un repo git válido y `git rev-parse` CLI funciona; falla SOLO dentro del
proceso `gbrain serve` (MCP del harness) cuando el bridge delega el sync por el lock
PGLite. `discoverGitRoot` usa `silenceStderr` y mascara el error git real.
- **Causa raíz**: el env del serve del harness hereda `GIT_DIR` apuntando a un `.git`
  ajeno; git resuelve contra ese y no contra el vault → el fallo se enmascara.
  Reproducir con `GIT_DIR=<path fake> git -C <vault> rev-parse --show-toplevel`.
- **`GIT_DIR=""` NO neutraliza**: git trata set-vacío como set → también rompe.
  Hay que UNSET o apuntar al `.git` real del vault.
- **FIX APLICADO (duradero)**: el bridge ahora hace `env.pop("GIT_DIR")` y
  `env.pop("GIT_WORK_TREE")` antes de lanzar `gbrain sync`, y fija
  `OLLAMA_BASE_URL` local con override (no `setdefault`). No hace falta matar el
  serve ni tocar config global. Si reaparece, revisar que el bridge en uso sea la
  versión con esos pops.

### Rutas de memoria del bridge (perfil-scoped)
El bridge resuelve su log auxiliar bajo `HERMES_HOME` (`$HERMES_HOME/data/
memory-references.jsonl`), NO en `~/.hermes/memory.jsonl` heredado. Para tests o
run aislado, exportar `HERMES_HOME`; nunca asumir el home antiguo. El log auxiliar
(`memory-references.jsonl`) NO es el `MEMORY.md` canónico — no lo leas como memoria
persistente ni lo consolides como si lo fuera.

### Consolidación diaria — escritura protegida
`consolidate` escribe SOLO dentro de una sección marcada
`<!-- hermes:consolidation:start|end -->`: preserva texto humano fuera de la
sección, es idempotente (dos corridas → mismo archivo), usa `filelock` + escritura
atómica (`mkstemp`+`os.replace`) y deja backup previo en `10-Diario/.hermes-backups/`.
Si la sección marcada está duplicada/malformada, el script falla en vez de
sobrescribir — no lo 'arregles' relajando esa guarda.

### Parser de salida de gbrain
`_extract_trailing_json` debe devolver el ÚLTIMO objeto JSON **exterior** completo
(walk forward con `JSONDecoder.raw_decode`, quedarse con el último dict top-level),
no el último objeto interior anidado. Un parser que devuelve el interior silencia
el `status` del payload y corrompe métricas aguas abajo.

## Vault

`C:\Users\<USER>\Documents\Obsidian Vault\`
Override: `OBSIDIAN_VAULT_PATH`