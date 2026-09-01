---
name: external-repo-adoption
description: "Adopt GitHub repos into Hermes: triage, port, verify."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [repo-adoption, porting, triage, github, skill-install, verification]
    related_skills: [port-external-pattern-to-hermes, third-party-skill-install, hermes-skill-integration, hub-skill-vetting]
---

# External Repo Adoption (GitHub → Hermes)

## When to Use

- User pega una URL de GitHub y pregunta "¿cómo adoptamos esto?", "¿para qué sirve?",
  "instálalo", "porta esto", "¿nos favorece?".
- Evaluar un repo de skill-pack, modelo, o "teoría/arquitectura" antes de instalarlo.
- Portar un skill data+scripts (CSVs + Python stdlib) de otro ecosistema a Hermes.

Regla de oro: **leer, aprender y CONSULTAR antes de ejecutar** — nunca instalar sin que
el usuario apruebe. El usuario ya lo pidió dos veces en una sesión (2026-08-27).

## Workflow (validado)

### 1. Triage rápido por GitHub API (decidir port vs knowledge vs skip)
```bash
curl -s https://api.github.com/repos/<owner>/<repo> | python -c "import json,sys; d=json.load(sys.stdin); print(d['pushed_at'], d['stargazers_count'], d['size'], d['license'])"
curl -s "https://api.github.com/repos/<owner>/<repo>/releases"   # 0 releases ≈ sin artefactos
curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1" | grep -iE "safetensor|ckpt|checkpoint|weights|\.bin"  # buscar pesos
curl -s "https://api.github.com/repos/<owner>/<repo>/commits?per_page=5"  # actividad
```
Señales de "repo de referencia, no producto": 0 releases + sin pesos + árbol pequeño +
commits viejos + web_search confirma hype sin sustancia.

### 2. Tres salidas posibles
- **Skip** — hype puro, sin valor para el stack (repo muerto, sin artefactos, decoración).
- **Knowledge skill** — repo "teórico" SIN artefacto usable (sin pesos/data/scripts): crear
  skill de conocimiento con 8 secciones: veredicto honesto, arquitectura ASCII, mecanismos
  clave, research grounding, takeaways, pitfalls verificados con fecha, smoke test
  reproducible, regla de oro. Ej: OpenMythos → `openmythos-rdt`.
- **Port completo** — repo con data + scripts stdlib + templates por plataforma: ver
  `references/port-recipes.md` §B para el recipe exacto (ui-ux-pro-max).

### 3. Verificación (nunca marcar "validado" sin ejecución real)
- Correr la suite del repo DESDE el dir instalado, excluyendo tests que asumen el layout
  del repo git (buscan la raíz en `Path(__file__).resolve().parents` → StopIteration):
  `python -m pytest scripts/tests/ -q --ignore=scripts/tests/test_catalog_refresh.py`
- Tratar "stale catalog snapshot vs upstream" como check CI de publicación, no bug funcional.
- Smoke test independiente de cada entry point; NO confiar en el README del repo (sus
  ejemplos pueden tener bugs contra el código real).
- `skill_view(name=...)` → `readiness_status == "available"`.

## Pitfalls

- **skill_manage create**: description ≤60 chars (trigger first, termina en punto) y sección
  `## When to Use` obligatorias — la creación falla/reclama si no. Adaptar frontmatter al budget.
- **Bug de rutas Windows**: componer SKILL.md con terminal python heredoc y rutas forward-slash
  (`C:/...`); write_file con rutas absolutas `/c/...` duplica el prefijo `C:\c\`.
- **No portar decoración**: CLI installers, plugins del ecosistema (.claude-plugin), gallery,
  screenshots — el `templates/platforms/universal.json` del repo marca la frontera del skill.
- **Repos user-owned en la biblioteca**: varios umbrellas de esta clase viven como
  user-owned (created_by=None) y NO se pueden editar en curaduría autónoma — recomendar
  `hermes curator adopt <name>` al usuario.

## Support files
- `references/port-recipes.md` — recipes verificadas (2026-08-27): knowledge-skill (OpenMythos)
  y port data+scripts (ui-ux-pro-max) con comandos exactos.
- `references/agent-tool-adoption.md` — recipe verificada (2026-09-01) para adoptar un
  PRODUCTO de agente (CLI + extensión/skill por harness, no un port de data/scripts).
  Ejemplo: BrowserSkill (Tencent) — `bsk install-skill --harness hermes`, verificación con
  `bsk doctor`, registro en índice Pulpo + EVOLUTION.md, y el único paso humano (extensión).
- `references/skill-pack-adoption.md` — recipe verificada (2026-09-01) para adoptar skills
  de un skill-pack (`npx skills add` con múltiples SKILL.md): clonar, filtrar por
  auth/key + redundancia + corre-en-este-entorno, portar SOLO los ganadores a Hermes.
  Ejemplo: ReScienceLab/opc-skills → solo se adoptó `seo-geo` (audit SEO/GEO sin API).
