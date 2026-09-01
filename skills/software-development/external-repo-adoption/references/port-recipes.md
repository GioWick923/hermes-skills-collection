# Port Recipes (sesiones verificadas, 2026-08-27)

## Recipe A: Repo "teórico" sin artefacto usable → skill de conocimiento (OpenMythos)

Contexto: `kyegomez/OpenMythos` — "theoretical reconstruction" de la arquitectura Claude Mythos.
14.8k★, 0 releases, sin pesos entrenados, último commit 3 meses antes de la verificación.

### Triage rápido por GitHub API (antes de decidir port vs knowledge)
```bash
curl -s https://api.github.com/repos/<owner>/<repo> | python -c "import json,sys; d=json.load(sys.stdin); print(d['pushed_at'], d['stargazers_count'], d['size'], d['license'])"
curl -s "https://api.github.com/repos/<owner>/<repo>/releases"   # 0 releases = casi seguro sin artefactos descargables
curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1" | grep -iE "safetensor|ckpt|checkpoint|weights|\.bin"  # buscar pesos
curl -s "https://api.github.com/repos/<owner>/<repo>/commits?per_page=5"  # actividad reciente
```
Señales de "repo de referencia, no producto": 0 releases + sin archivos de pesos + árbol pequeño
+ commits viejos. Verificar también community verdict con web_search (ej: "OpenMythos review").

### No confiar en el README del repo
El ejemplo del README de OpenMythos hacía `torch.linalg.eigvals(A)` sobre un tensor diagonal 1-D
→ RuntimeError (eigvals exige 2-D). Para matriz diagonal, los eigenvalores son los elementos:
`A.abs().max()`. Regla: verificar cada claim del README con ejecución propia antes de documentarlo.

### Suite del repo puede tener bugs de fixtures
OpenMythos: 63/75 tests pasaban; 12 fallaban por la MISMA causa (pasaban freqs completas a
atención cuando `apply_rope` exige freqs cortadas a las posiciones exactas — el modelo real
sí cortaba). Documentar el diagnóstico exacto (bug de test, no de código) en el skill.

### Entregable: skill de conocimiento con 8 secciones
1. Veredicto honesto (qué es / qué NO es, con fecha de verificación)
2. Arquitectura en ASCII
3. Mecanismos clave (lo absorbible)
4. Research grounding (papers con fechas)
5. Takeaways para el stack local
6. Pitfalls verificados con fecha
7. Smoke test reproducible (código listo para correr)
8. Regla de oro

## Recipe B: Port completo de skill data+scripts (ui-ux-pro-max)

Contexto: `nextlevelbuilder/ui-ux-pro-max-skill` v2.13.0 (MIT, 122k★, activo — push el mismo día).
Repo de ~30MB con data CSVs + scripts Python stdlib + templates por plataforma + CLI (no portar).

### Pasos validados
1. Clone a staging: `git clone --depth 1 <url> "$LOCALAPPDATA/Temp/uupm-src"`
2. Inspección por GitHub API (tree): contar archivos por directorio; buscar `skill.json` y el
   `templates/platforms/universal.json` del repo (dice el layout canónico del skill:
   SKILL.md + data/ + scripts/search.py).
3. Confirmar scripts stdlib puro: `grep -E "^(import|from)" scripts/core.py` →
   csv/difflib/re/pathlib = port directo, sin venv, sin red.
4. Componer SKILL.md con terminal python heredoc (rutas forward-slash `C:/...` — evita el bug
   de write_file con rutas absolutas `/c/...`): leer `templates/base/skill-content.md`,
   reemplazar placeholders (`{{TITLE}}`, `{{DESCRIPTION}}`, `{{QUICK_REFERENCE}}`, `{{SCRIPT_PATH}}`),
   anteponer frontmatter Hermes con **description ≤60 chars** (budget del índice) y sección
   `## When to Use`.
5. Copiar data/ y scripts/ (y tests si vienen) con `cp -r` al skill dir:
   `$LOCALAPPDATA/hermes/skills/<name>/`
6. Tests desde el dir instalado. **Pitfall: tests que asumen el layout del repo git** —
   `test_catalog_refresh.py` y `test_relevance_evaluator.py` lanzan StopIteration buscando la
   raíz del repo en parents. Excluir con `--ignore`. Resultado real: 129 pass + 7923 subtests;
   1 fallo = "stale catalog snapshot" (check de CI de publicación contra upstream, NO bug funcional).
7. Smoke tests por entry point: `--domain color`, `--stack shadcn`, `--design-system`,
   dials (`--variance 8 --density 7`), y generador vía `from design_system import generate_design_system`.
8. `skill_view(name=...)` → `readiness_status == "available"`; limpiar staging
   (`rm -rf "$LOCALAPPDATA/Temp/uupm-src"`); anotar en EVOLUTION.md.

Tamaño final típico: ~3.7MB (data CSVs ~3.1MB). Actualizar a futuro: re-clonar y re-copiar
data/ + scripts/ (no editar a mano: el repo usa sync automático desde `src/`).

### Qué NO portar
CLI (`npx ... init`), plugin del ecosistema (.claude-plugin), gallery/screenshots, docs de
contribución. El universal.json del repo marca la frontera: SKILL.md + data + scripts.
