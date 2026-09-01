---
category: productivity
name: make-it-stick-study-lab
description: "Crea laboratorio de estudio de 7 días (Make It Stick)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [study, learning, spaced-repetition, flashcards]
    related_skills: [teach, session-librarian, obsidian]
---

# Make It Stick Study Lab

Porte del prompt "Modificar el aprendizaje" (botdirectory/Grok Bot #13) adaptado
a Hermes. Convierte una carpeta de libros/notas en un laboratorio de práctica de
7 días basado en Make It Stick: recuperación, espaciado e intercalado.

## When to Use

- El usuario quiere aprender/dominar algo profundo (curso, libro, tema técnico).
- Tiene una carpeta local de PDFs, EPUBs o notas sobre el tema.

## Pasos

1. **Entrevista inicial**: qué carpeta usar, perfil (estudiante/adulto), qué
   materias practicar, día de inicio.
2. **Preparar** (mantener PDF/EPUB originales como solo lectura):
   - `scripts/gen_plan.py <carpeta>` genera la estructura del laboratorio:
     - `plan-7-dias.md` (cada día: tema + técnica + repaso espaciado)
     - `tarjetas/` (recuperación, formato CSV/markdown)
     - `calendario-revision.md` (repasos en día 1, 2, 4, 7)
     - `debilidades.md` (registro de fallos)
     - `mapa-4-cuadros.md` (qué sé / qué no sé / qué practicar / qué repasar)
3. **Día 1 supervisado**: ejecutar con el usuario — ocultar texto, escribir 2
   oraciones de memoria, programar la siguiente pregunta de repaso.
4. **Ejecución diaria**: cada día generar el kit del día (recuperación activa +
   tarjetas + mezcla de problemas de días anteriores).
5. **Revisión**: al día 7, consolidar debilidades y decidir siguiente ciclo.

## Reglas

- Nunca modificar los PDF/EPUB originales (carpeta es solo lectura para ellos).
- Recuperación primero: leer no cuenta como estudio; practicar sí.
- Espaciado: cada tema se repasa en al menos 3 días separados.
- Intercalado: mezclar tipos de problemas, no bloques de un solo tipo.

## Verificación

- [ ] Estructura del laboratorio generada (plan, tarjetas, calendario)
- [ ] Originales intactos (read-only)
- [ ] Día 1 ejecutado con el usuario
- [ ] Registro de debilidades actualizado tras cada práctica
