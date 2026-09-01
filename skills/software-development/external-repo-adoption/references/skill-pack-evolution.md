# Skill-Pack EVOLUTION (pack ya instalado) + plugin security-scanner fallback

Verificada 2026-09-01 (sesión de 5 skill-packs vía tweets: agent-skills, ui-ux-pro-max,
caveman, obsidian-skills, nuwa-skill). Dos escenarios nuevos respecto a skill-pack-adoption.md.

## Escenario A: EVOLUCIÓN de un skill-pack YA instalado en Hermes

Cuando el usuario pide analizar un skill-pack y **ya está instalado**, NO reinstalar a ciegas:
el repo upstream puede estar más nuevo (drift) pero la copia local puede tener
**modificaciones propias valiosas** que no se deben perder.

### Paso 1: diff sistemático por skill (nunca a ojo)
```python
# para cada skill del pack: comparar local vs repo
h = open(HERMES/s/SKILL.md).read(); r = open(REPO/s/SKILL.md).read()
if h == r: idéntica
else: # contar líneas solo-en-local (modif propia) vs solo-en-repo (repo más nuevo)
  only_local = set(h.splitlines()) - set(r.splitlines())
  only_repo  = set(r.splitlines()) - set(h.splitlines())
```
Clasificar cada skill en 4 buckets:
- **idéntica** → no tocar
- **repo más nuevo** (+muchas líneas solo-en-repo) → candidata a actualizar
- **modificación local propia** (+líneas solo-en-local) → PRESERVAR, no sobrescribir
- **diferencias menores** (1-3 líneas) → casi siempre son rutas de referencia ya adaptadas
  a Hermes (`references/` vs `../../references/` del repo) — NO tocar, mi adaptación es correcta

### Paso 2: añadir skills que faltan + traer carpeta references/ compartida
El repo suele tener una carpeta `references/` raíz con checklists compartidos que las skills
referencian (`../../references/xxx.md`) y que la instalación local quizá no trajo. Copiarla
entera a `HERMES/pack/references/` y normalizar las rutas en los SKILL.md actualizados:
```python
txt = txt.replace("../../references/", "references/")
```

### Paso 3: verificación post-evolución
Escaneo de rutas rotas: buscar refs `../../references/` sin normalizar + refs a
`references/xxx.md` que no existan. ⚠️ FALSO POSITIVO conocido: una skill puede referenciar
`references/floor-guard.md` que vive en SU subcarpeta `skill/references/` (no en la compartida) —
el script de verificación no debe asumir que toda referencia resuelve en la carpeta raíz.
Comprobar ambas ubicaciones antes de marcar roto.

### Ejemplo real (agent-skills / addyosmani, v0.6.8)
- 24 skills instaladas → repo tiene 25. Faltaba `constraint-driven-development`.
- 6 desactualizadas (repo más nuevo: api-and-interface +47l, performance +68l, security +29l,
  source-driven +16l, spec-driven +29l, planning). Actualizadas con rutas normalizadas.
- planning-and-task-breakdown tenía +7 líneas propias (convención `tasks/plan.md`) — el repo
  en realidad la DESARROLLA de forma más completa, así que adoptar la versión repo fue seguro.
- Traída carpeta `references/` compartida (7 checklists) que faltaba.
- Resultado: 25 skills + references, sin rutas rotas.

## Escenario B: `hermes plugins install` BLOQUEADO por el escáner de seguridad

Síntoma: `hermes plugins install <url>` falla con veredicto "BLOCKED — dangerous verdict,
community source, N findings". `--force` NO lo sobreescribe en veredicto dangerous.

### Fallback correcto (NO instalar el plugin)
El valor real de un skill-pack suele estar en los **SKILL.md** (markdown puro), no en el
código del plugin (scripts/hooks/commands). Cuando el bundle está bloqueado:
1. Clonar el repo, ir a `skills/<nombre>/SKILL.md`.
2. Portar SOLO los SKILL.md (markdown, cero ejecución de código del paquete) a
   `$LOCALAPPDATA/hermes/skills/<nombre>/SKILL.md` con `write_file`, adaptando el
   frontmatter a Hermes (categoría, versión 1.0.0, tags, nota de integración).
3. NO copiar scripts/hooks/evals del repo (mismo criterio de riesgo que motivó el bloqueo).
4. Registrar en índice Pulpo + EVOLUTION.md.

### Ejemplos reales (2026-09-01)
- **Ponytail** (DietrichGebert/ponytail): plugin bloqueado (comunidad, 83 findings). Se portó
  solo `skills/ponytail/SKILL.md` → skill `ponytail` en Hermes. Funciona.
- **caveman** (JuliusBrussee/caveman): solo el skill principal (markdown puro); se EVITÓ
  `caveman-compress` (llama a Claude externo). Complementa a ponytail (mismo autor).
- **obsidian-cli** (kepano/obsidian-skills): markdown puro; documentado como complemento al
  bridge hermes_obsidian_bridge.py (bridge no requiere Obsidian abierto; CLI sí).

## Decisión total / parcial / evolución / skip (marco que pidió el usuario)
| Parámetro | Cuándo |
|-----------|--------|
| **Integrar** | skill markdown puro, sin keys, alto valor, no existe en Hermes, alineada con preferencias |
| **Evolución parcial** | pack ya instalado, repo más nuevo → diff, actualizar ganadores, preservar mods locales |
| **Adaptar (marco ligero)** | proyecto valioso pero pesado/costoso (multi-agente, $) → portar SOLO el marco conceptual |
| **Skip** | requiere keys/tokens externos, redundante con skills existentes, o infra no portable |

Ejemplo de "adaptar marco ligero": **nuwa-light** — la versión completa de nuwa-skill usa
6 agentes + 500k tokens + decenas de $. Se portó solo el marco conceptual
(extraction-framework + skill-template + fidelity-scorecard) como skill ligera que corre con
1 web_search por dimensión. Aplica también el mismo criterio a infra no portable
(CubeSandbox = RustVMM/KVM, Linux-only → no se miniaturiza, se descarta como candidato futuro).
