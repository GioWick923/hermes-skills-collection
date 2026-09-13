---
category: hermes-self-evolution
name: hermes-self-evolution
description: "Evolucion auto-optimizadora de skills/prompts de Hermes Agent usando DSPy + GEPA (NousResearch, ICLR 2026). NO se auto-ejecuta: requiere 'pip install -e .' de sus dependencias (dspy, gepa) y un HERMES_AGENT_REPO apuntado. Usar solo cuando el usuario pida 'evolucionar/optimizar un skill', 'mejorar SKILL.md con GEPA', o 'self-evolution'. Herramienta pesada (~$2-10 por run via API)."
version: "0.1.0"
---

# hermes-self-evolution (wrapper)

Paquete oficial de NousResearch para auto-mejorar skills de Hermes vía
evolucion evolutiva (DSPy + GEPA). El codigo esta en `./repo/`.

## ⚠️ Estado: NO auto-cargable
Esta skill NO se ejecuta sola. Requiere dependencias de terceros (dspy>=3.0.0,
gepa) que no estan instaladas para no contaminar el entorno. Para activarla:

```bash
cd "$LOCALAPPDATA/hermes/skills/hermes-self-evolution/repo"
pip install -e ".[dev]"          # instala dspy, gepa, etc.
export HERMES_AGENT_REPO="$LOCALAPPDATA/hermes/hermes-agent"
```

## Uso (una vez activada)
```bash
# Evolucionar un skill con datos de evaluacion sinteticos
python -m evolution.skills.evolve_skill --skill github-code-review --iterations 10 --eval-source synthetic

# O usar historial de sesiones reales
python -m evolution.skills.evolve_skill --skill github-code-review --iterations 10 --eval-source sessiondb
```

## Fases implementadas
- Phase 1: Skill files (SKILL.md) — DSPy + GEPA ✅
- Phase 2-5: tool descriptions, system prompt, codigo, loop continuo — planeado

## Costo
~$2-10 por run de optimizacion (solo llamadas API, sin GPU).

## Notas de seguridad
- Escribe/propone cambios de codigo (genera PRs contra hermes-agent).
- No se ejecuta automaticamente; requiere aprobacion explicita del usuario.
- Ver SKILL.md original en ./repo/README.md para detalles completos.
