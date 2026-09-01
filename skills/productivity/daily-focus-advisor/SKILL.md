---
category: productivity
name: daily-focus-advisor
description: "Plan diario de enfoque: bloques realistas y qué aplazar."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [focus, calendar, planning, daily]
    related_skills: [google-workspace, weekly-review-planning, agent-operating-manual]
---

# Daily Focus Advisor

Porte del prompt "Asesor de enfoque diario" (botdirectory/Grok Bot #23), adaptado
a Hermes. Cada mañana revisa compromisos y prioridades, y propone el plan de
enfoque del día con bloques realistas y qué aplazar.

## When to Use

- Cada mañana, cuando el usuario pida "plan del día", "qué hago hoy", "enfócame".
- Al arrancar la semana, para planificar bloques de enfoque.

## Pasos

1. **Entrevista inicial (una sola vez)**: preguntar al usuario:
   - Objetivos activos (proyectos, metas).
   - Compromisos inamovibles de esta semana (no negociables).
   - Horario preferido de trabajo (ej. 9-13 enfoque, 15-18 admin).
   - Qué tipos de trabajo merecen prioridad (deep work vs operativo).
2. **Fuentes de datos**:
   - Google Calendar → skill `google-workspace` (gws calendar list / agenda de hoy).
   - Proyectos/TODO → gbrain, Obsidian vault, o memoria operativa.
3. **Generar plan**: bloques de enfoque de 90 min con 1 tarea principal por bloque;
   máximo 3 bloques de deep work al día; separar admin; nombrar explícitamente
   QUÉ se aplaza y por qué.
4. **Dry-run supervisado**: primer plan se muestra completo para corrección.
5. **Programar**: opcional, `hermes cron add` diario (ej. `30 7 * * 1-5`).
6. **Verificación**: al final del día, 1 línea: qué se completó, qué se movió.

## Salida (formato)

```
🎯 Hoy — <fecha>
1. [90m] Tarea A (proyecto X) — 9:00-10:30
2. [90m] Tarea B — 11:00-12:30
   ...
⏸️ Aplazar: <cosas> porque <razón>
📋 Admin: <lista corta> (15:00-15:45)
```

## Reglas

- Nunca inventar compromisos del calendario; si no hay fuente conectada, decirlo.
- El plan es propuesta: el usuario siempre puede reordenar.
- Revisar quincenalmente si los bloques son realistas (sobre-planificar = fallar).

## Verificación

- [ ] Fuente de calendario consultada (o gap declarado)
- [ ] Plan con bloques + aplazamientos explícitos
- [ ] Dry-run aprobado antes de programar cron
