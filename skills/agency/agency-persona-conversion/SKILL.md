---
name: agency-persona-conversion
description: "Procedimiento para convertir librerías de personas/agentes externas (p.ej. msitarzewski/agency-agents, MIT, ~147 agentes) en skills de Hermes: clonar, leer definiciones reales, destilar a SKILL.md con prefijo/ categoría, mapear 'spawn agent' a delegate_task, y verificar sin romper nada."
platforms: [linux, macos, windows]
category: agency
---

# Conversión de librerías de personas (Agency Agents) → skills de Hermes

Clase de trabajo: tomar un catálogo de agentes externos (definidos como `.md`
con frontmatter YAML + secciones `Identity`/`Mission`/`Critical Rules`) y
convertirlos en `SKILL.md` de Hermes, organizados como un equipo multiagente
que se orquesta vía `delegate_task`. También cubre la verificación y
reorganización segura del árbol de skills.

## Cuándo usar
- El usuario pide volcar/adaptar un repo de "AI agents personas" (Agency Agents,
  similares) a skills de Hermes.
- Necesitas extender el pack `agency/*` o crear un equipo multiagente desde cero.
- Necesitas verificar/consolidar skills sin romper resolución por `name`.

## Pasos de conversión
1. **Clonar y leer las definiciones reales** (nunca resumir de oídas):
   ```bash
   git clone --depth 1 https://github.com/msitarzewski/agency-agents.git
   ls agency-agents/engineering   # catálogo de agentes por división
   ```
2. **Un skill por agente**, carpeta `agency/<rol>/SKILL.md`. Frontmatter:
   ```yaml
   ---
   name: agency-<rol>          # prefijo obligatorio: filtra y evita colisiones
   description: "<Rol> (Agency Agents → Hermes). <qué hace, 1 línea>."
   platforms: [linux, macos, windows]
   category: agency            # habilita skills_list(category='agency')
   ---
   ```
3. **Destilar, no traducir literal**: conserva `Critical Rules`, trade-offs y
   entregables; elimina el lock-in de stack del original (p.ej. Laravel/Livewire
   → "agnóstico al stack, usa las herramientas del proyecto").
4. **Mapear "spawn agent X" → `delegate_task`** en el orquestador:
   ```python
   delegate_task(goal="...", role="leaf",
                 toolsets=["terminal","file","web"])  # + ["browser"] para QA visual
   ```
5. **Referencias entre skills por `name`** (ej. `agency-architect`), NUNCA por ruta
   de carpeta (ver "Principio de organización").

## Principio de organización (no romper nada)
- Skills se resuelven por `name:` en el frontmatter, NO por ruta de directorio.
  Mover/renombrar carpetas es seguro mientras no cambies el `name`.
- Agrupar por `category` en frontmatter para filtrar con `skills_list(category=...)`.
- Consolidar carpetas duplicadas (ej. `mlops-inference/` → `mlops/inference/`) con
  `mv`; luego verificar que las viejas rutas desaparecieron y las nuevas existen.
- Antes de mover: `grep -rn "<nombre-carpeta>"` para confirmar que nada fuera de
  `skills/` referencia la ruta.

## PITFALLA: registrar el skill
Crear `SKILL.md` directo a disco (sin `skill_manage create`) deja el skill SIN
registrar en el perfil activo. Síntoma: `skill_view` lo carga, pero
`skill_manage write_file/patch` falla con "not found in active profile".
Corrección: registrar vía la creación del skill en el perfil, o bien no depender
de `skill_manage` para skills en disco (editar con `patch` del agente tras
registrarlos). Para adjuntar `references/`, el skill debe estar registrado.

## Script de verificación ad-hoc (tolerante a YAML mal formado)
Skills externos pueden tener frontmatter YAML inválido (apóstrofes sin escapar).
Usar regex, NO `yaml.safe_load`, para no crashear. Guardar en
`%TEMP%/hermes-verify-*.py`, correr con el python del venv, borrarlo.

```python
import os, glob, re, sys
base = "C:/Users/<USER> GAMES/AppData/Local/hermes/skills"
bad = False
for f in sorted(glob.glob(os.path.join(base, "agency", "**", "SKILL.md"), recursive=True)):
    t = open(f, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    if not m: print("FAIL frontmatter", f); bad = True; continue
    fm, body = m.group(1), m.group(2)
    nm = re.search(r"^name:\s*(.+)$", fm, re.M)
    ct = re.search(r"^category:\s*(.+)$", fm, re.M)
    name = nm.group(1).strip().strip('"\'') if nm else None
    cat = ct.group(1).strip() if ct else None
    if not (name and name.startswith("agency-") and cat == "agency" and len(body.strip()) > 50):
        print("FAIL", name); bad = True
print("RESULT:", "ALL PASS" if not bad else "FAILURES")
sys.exit(0 if not bad else 1)
```
Venv: `C:/Users/<USER> GAMES/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`
(Es verificación de estructura/contenido, NO de ejecución de pipeline.)

## Cómo extender el equipo
- Añadir `agency-<nuevo-rol>/SKILL.md` con el frontmatter de arriba.
- Registrarlo en `agency/orchestrator/SKILL.md` (sección "Agentes disponibles")
  y en `agency/README.md` (tabla de índice).
- Correr el script de verificación.
