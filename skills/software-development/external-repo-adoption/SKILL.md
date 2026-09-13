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

### 2b. Cuarta salida: "Infra/platform → NO adoptar" (lección 2026-09-01)
Hay repos impresionantes que son **infraestructura o plataforma, no skills adoptables**. La
señal: el repo despliega un runtime/servicio (virtualización, control-center web, sandbox)
que **duplica capacidades que el stack de Hermes ya cubre** (MCP, skills, cron, memoria,
delegación, browser real). No es ni skip (tiene valor real) ni port (no es un skill):
la decisión correcta es **evaluar honestamente y NO instalar** (over-engineering, regla
ponytail). Pero extraer el PATRÓN de diseño como skill de conocimiento sí vale.

Casos reales 2026-09-01:
- **Loop Rat (mrbuzzoni/loop-rat)**: harness bash/python de "shifts" autónomos nocturnos
  (schedule.yml + CONTRACT.md + guard + grader + receipts). 0⭐, MIT. Verificado 2026-09-03:
  suite propia → 91/129 FAILS en Windows git-bash (signal.SIGPIPE no existe en Windows,
  crontab, locks POSIX, hardcode `python3`). Diseñado para CLI `claude` (no instalado aquí).
  Duplica 100% capacidades Hermes nativas: cron jobs, autonomy-engine, self-reflect/validate-output,
  Obsidian receipts, spend caps. → NO instalar; el patrón "preflight→act→verify→guard→grade→receipt"
  ya vive en automation-workflow-patterns + autonomy-engine.
- **CubeSandbox (TencentCloud)**: sandbox MicroVM por KVM para ejecutar código de agents.
  Infra pesada (KVM/containerd/eBPF/Redis, Linux-only) que no corre en Windows y duplica
  Docker+local. → NO instalar; documentar el concepto snapshot/fork/rollback como patrón.
- **OpenHands Agent Canvas**: control-center web para agents (Agent Server + Automation
  Server + Slack/GitHub/Linear). Casi todo ya cubierto por Hermes (MCP/skills/cron/webhooks).
  → NO instalar; extraer solo el patrón "script-bundle + agente solo-para-juicio" → skill
  `automation-workflow-patterns`.

Cómo decidir: pregúntate "¿esto es un skill/procedimiento, o un servicio/runtime?" + "¿el
stack actual ya lo resuelve?" — si ambas señales son "servicio" y "sí", no adoptes; extrae
solo el patrón reutilizable.

**Cuando el usuario dice "porta la idea"** (loop-rat → shift_guard/blind_grade, verificado
2026-09-03): NO se copia el harness — se leen los 2-3 archivos core del repo, se reescriben
como scripts propios limpios para el host (stdlib, sin SIGPIPE/crontab/python3 hardcode),
se prueban contra un scratch git repo con casos de borde, y se enganchan a la skill
gobernante + registro. Recipe completa: `references/pattern-port-to-own-scripts.md`.

### 2c. Quinta salida: "Ya está integrado en mis propias tools" (verificado 2026-09-03)
Antes de triagear el árbol del repo, compara los NOMBRES de helpers/entrypoints del repo
contra las herramientas que YA tienes cargadas. Caso: **browser-use/browser-harness**
(17.4k⭐) — `page_info/new_tab/goto_url/agent_helpers.py/BH_AGENT_WORKSPACE` son EXACTAMENTE
los que pre-importa `browser_exec` de Hermes: el repo ES el backend de la tool; instalarlo
aparte = duplicado. Check barato: `grep -o 'def [a-z_]*' <repo>/src/*.py` vs el docstring
de tu tool. La acción útil fue diagnosticar config del real-profile — recipe completa en
`references/browser-harness-real-profile-windows.md` (default OS Chromium vía ProgId,
`real_profile_pin` = DIR de perfil no navegador, handoff de 2 clics en Win11 para
default-browser e import de Chrome, verificación con conteos sqlite).

### 2d. Regla anti-"dedo fantasma" (mensajes vacíos)
Si el usuario manda "." o mensaje vacío 2+ veces, NO asumas ruido: puede ser envío roto o
confusión. Re-pitch breve con la decisión pendiente en forma A/B y sigue con lo que SÍ
llegó adjunto en el siguiente turno (puede ser el siguiente repo de la fila).

### 2e. Sexta salida: "Skill-wrapper de SaaS → prueba la ruta LOCAL primero" (2026-09-03)
El repo es 12 SKILL.md que envuelven una API de terceros con key + créditos
(caso: ZeroPointRepo/youtube-skills → TranscriptAPI). Antes de registrar cuenta ajena:

1. Lista las capacidades del menú del SaaS (transcript/search/canal/playlist/etc.).
2. Corre la equivalencia local YA instalada (yt-dlp, youtube-transcript-api, curl) contra
   cada capacidad, en el host real. El pitch "YouTube bloquea cloud IPs" no aplica a
   máquina residencial.
3. Si local cubre ~100% → NO instalar el wrapper. Adaptar a la skill local existente:
   (a) las RECETAS exactas verificadas, (b) el TRIGGER description del repo (suele ser
   mejor que el propio — "aunque no se mencione X"), (c) patrones de ingeniería del
   auth-setup (p.ej. anti-redacción de tokens: response→archivo→siguiente request,
   nunca imprimir sk_/access_token), (d) el SaaS queda documentado como fallback.
4. Bonus frecuente: leer el setup del repo expone bugs de TU skill (uv run roto en el
   host → fix a rutas de venv directo) — páchalos en el mismo paso.

### 2f. Convención de registro post-adopción (corrección del usuario 2026-09-03)
"Regístralo en tus herramientas" + "para que sepas que lo tienes cuando hagas un trabajo"
= el registro debe ser VISIBLE AL TRABAJAR, no solo archivado. Cuatro destinos, en orden:
1. **Índice de Capacidades Pulpo** (vault `50-Indice/`): tabla de scripts + sección con
   fuente/protocolo/verificación + **fila en la tabla de decisión "¿qué extremidad uso?"**
   (esta es la que se consulta en caliente).
2. **EVOLUTION.md** bitácora.
3. **Bridge remember** (`hermes_obsidian_bridge.py remember --category decision`).
4. **Memoria built-in de Hermes** (la que se inyecta en CADA sesión): puntero corto al
   índice + claves operativas. Sin este paso el usuario tiene que recordarte buscar —
   con él, la regla aparece sola en el contexto del turno. Presupuesto apretado:
   consolida/replace entradas viejas en el mismo batch.

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
- `references/skill-pack-evolution.md` — recipe verificada (2026-09-01) para EVOLUCIONAR un
  skill-pack ya instalado (addyosmani/agent-skills): diff skill por skill, actualizar solo las
  desactualizadas, añadir las faltantes, traer references/ compartidas, preservar rutas ya
  adaptadas y convenciones locales (tasks/plan.md).
- `references/plugin-blocked-port-markdown.md` — recipe verificada (2026-09-01) para cuando
  `hermes plugins install` bloquea un repo de comunidad (veredicto dangerous) pero los SKILL.md
  son markdown puro y valioso: portar solo los SKILL.md a Hermes, sin scripts del paquete.
  Ejemplo: Ponytail.
- `references/infra-platform-no-adopt.md` — recipe verificada (2026-09-01) para repos que son
  infra/plataforma (no skills): señales de decisión, casos CubeSandbox (KVM sandbox) y Agent
  Canvas (control-center), y qué patrón extraer en cada caso.
- `references/pattern-port-to-own-scripts.md` — recipe verificada (2026-09-03) para "porta la
  idea": reescribir los patrones core de un repo no-instalable como scripts propios limpios
  (loop-rat → shift_guard.py + blind_grade.py), con suite de casos de borde en scratch repo.
- `references/omp-evaluation.md` — evaluación de OMP (oh-my-pi, 30k+ stars): por qué no adoptar,
  cuándo reconsiderar, comparación con Hermes.
