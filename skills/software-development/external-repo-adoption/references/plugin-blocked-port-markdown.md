# Plugin bloqueado por escáner de seguridad → portar solo SKILL.md

> Recipe verificada (2026-09-01) con Ponytail (DietrichGebert/ponytail) y evaluada en
> los 5 repos de skills del día. Cuándo usar: un repo de skills/plugins que el escáner de
> seguridad de Hermes bloquea al instalar como plugin, pero cuyo CONTENIDO (los SKILL.md)
> es markdown puro y valioso.

## El problema
`hermes plugins install <repo>` corre un escáner de seguridad. Para fuentes de comunidad con
muchos scripts/tests (JS/TS/Rust), puede devolver veredicto **dangerous** (ej. "Blocked —
community source + dangerous verdict, 83 findings") y **`--force` NO lo anula**. Los hallazgos
son en su mayoría LOW/MEDIUM en docs/tests/scripts — el SKILL.md en sí suele estar limpio.

## Por qué portar solo los SKILL.md es la jugada correcta
- Los SKILL.md son **markdown puro** — instrucciones, sin ejecución de código del paquete.
- El valor real de un skill-pack está en el conocimiento procedural (la escalera, el flujo),
  no en los scripts que trae el repo.
- Evita el riesgo de ejecutar scripts de un repo de comunidad no auditado.

## Workflow (verificado con Ponytail)
1. Clonar el repo: `git clone --depth 1 <repo> ~/tools/<name>`
2. Localizar los SKILL.md: `find <repo> -name SKILL.md`
3. Elegir cuáles portar: solo el(s) skill(s) con valor neto, alineado con el stack, SIN
   dependencias externas que fallen en el entorno (ej. una skill que llama a Claude externo).
4. Crear el skill en Hermes con `write_file` a `$LOCALAPPDATA/hermes/skills/<cat>/<name>/SKILL.md`,
   adaptando: frontmatter Hermes (category, author "Hermes Agent (port from ...)", license,
   versión 1.0.0), `python` en vez de `python3` (Windows), quitar deps rotas, sección de
   integración con el usuario.
5. **Moverlo a carpeta-categoría física** si no está en subdirectorio (ver pitfall del builder
   en `hermes-skills-publication`).
6. Verificar: `hermes skills list | grep <name>` → `enabled`.
7. Registrar en índice Pulpo (vault) + EVOLUTION.md.

## Criterio de selección de skills de un pack
- ✅ Solo skills que corren sin API key externa, sin herramienta que falle en el entorno.
- ✅ Priorizar los que llenan un hueco real (nada similar instalado).
- ❌ Descartar: los que requieren keys/tokens (twitterapi.io, ProductHunt, Gemini),
  los que duplican skills existentes, los que llaman servicios externos pagados.
- Ejemplo del día: de 10 skills de opc-skills, solo `seo-geo` (audit SEO/GEO sin API);
  de ponytail, solo el skill principal (no `caveman-compress` que llama a Claude).

## Pitfalls
- `--force` NO pasa por encima de un veredicto dangerous — no intentarlo.
- Un skill en la raíz de `skills/` (sin carpeta-categoría) no se publica al repo — muévelo.
- No portar los scripts del pack si no los vas a usar; el SKILL.md es autocontenido.
- Distinguir el veredicto del escáner (bloquea el PLUGIN) del valor del CONTENIDO (markdown).
