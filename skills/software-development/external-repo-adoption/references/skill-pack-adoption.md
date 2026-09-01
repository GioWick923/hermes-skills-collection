# Skill-Pack Adoption (repo de múltiples SKILL.md, estilo `npx skills add`)

Clase distinta de `port-recipes.md` (Recipe A knowledge / Recipe B data+scripts) y de
`agent-tool-adoption.md` (producto CLI+extensión). Aquí el repo es un **skill-pack**:
decenas de SKILL.md prefabricados instalables con `npx skills add <owner>/<repo>`
(Claude Code/Cursor/Codex, etc.). NO se instala el paquete entero: se **evalúan** sus
skills y se portan solo los que aportan valor real sin fricción.
Ejemplo verificado (2026-09-01): **ReScienceLab/opc-skills** → solo se adoptó `seo-geo`.

## Cuándo
- El usuario manda un tweet/repo de un "skill-pack para solopreneurs / X tarea" instalable
  con `npx skills add`.
- El paquete declara soporte para Claude Code/Cursor/Codex/otros — NO necesariamente Hermes.
- Hay que decidir CUÁLES de sus skills valen la pena (casi nunca todas).

## Workflow validado

### 1. Leer el tweet/repo, identificar el paquete
- Tweet → `read-x-tweet` (syndication) para el texto/contexto; el link del repo suele venir
  cortado en el extracto → buscar en web por el nombre + `github`.
- `skills.sh/<owner>/<repo>` da el catálogo (nº skills, total installs).

### 2. Clonar y listar el catálogo real
```bash
git clone --depth 1 https://github.com/<owner>/<repo> ~/tools/<repo>
ls ~/tools/<repo>/skills/                     # los skills reales
cat ~/tools/<repo>/skills.json | python -c "import json,sys; [print(s['name'],'| auth=',s.get('auth',{}).get('required'),'|',s['description'][:90]) for s in json.load(sys.stdin)['skills']]"
```
`sills.json` (o equivalente) dice: nombre, versión, descripción, `auth.required`,
`dependencies` entre skills. Ese es el filtro rápido.

### 3. Filtrar por 3 criterios (casi nunca pasar los 3)
1. **¿Requiere API key/token externo?** (`auth.required: true` → twitterapi.io, ProductHunt,
   Gemini, RequestHunt, DataForSEO...) → descartar salvo que el usuario ya tenga la key.
2. **¿Ya está cubierto por una skill Hermes existente?** (reddit vs `last30days`/
   `social-platform-trend-research`; archive vs memory/observational) → descartar redundancia.
3. **¿Corre en este entorno sin fricción?** → PROBAR con ejecución real, no asumir:
   ```bash
   cd <repo>/skills/<name> && timeout 40 python scripts/<entry>.py ...  # python, NO python3 (Windows)
   ```
   Si da error de entorno/403/network, descartar (no portar una skill que no corre).

### 4. Portar SOLO los ganadores a Hermes
- Copiar `scripts/` + `references/` + `examples/` del skill ganador a
  `$LOCALAPPDATA/hermes/skills/<name>/`.
- Escribir SKILL.md propio adaptado: frontmatter Hermes (description con trigger primero,
  ≤60 chars en el índice), `## When to Use`, workflow, verificación, pitfalls.
- **Adaptar a Windows:** `python` no `python3`; rutas con `$LOCALAPPDATA/...`; quitar
  dependencias del paquete que no se portan (p.ej. OPC seo-geo dependía de twitter/reddit
  → apuntar a las skills Hermes propias).
- Verificar desde la ruta instalada: `python "$LOCALAPPDATA/hermes/skills/<name>/scripts/<x>.py" "<url>"`.

## Pitfalls
- **No instalar el paquete entero** con `npx skills add` — ese CLI apunta a Claude/Cursor/
  Codex, y meter 10 skills de golpe ensucia la biblioteca. Portar a mano los ganadores.
- **El catálogo miente sobre lo que corre**: `auth.required: false` no garantiza que el
  endpoint no dé 403 (reddit → HTTP 403 en este host). Siempre prueba real.
- **Windows:** `python3` no existe; usar `python` (3.11). Si un skill dice `python3`, portar
  el script y probar con `python`.
- Skills con dependencias cruzadas internas del paquete (p.ej. `seo-geo`→`twitter`+`reddit`)
  pierden esas deps al portar solas; sustituirlas por la skill Hermes equivalente.

## Registro (convención Gio)
Sección nueva en el índice Pulpo del vault (`50-Indice/Indice de Capacidades Pulpo.md`)
+ entrada en `EVOLUTION.md` con el veredicto por skill (adoptada/descartada + por qué) +
repo fuente clonado en `~/tools/<repo>`.
