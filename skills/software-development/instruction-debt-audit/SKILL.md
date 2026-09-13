---
name: instruction-debt-audit
description: "Audit agent instruction debt: map 5 layers (descriptions, files, definitions, permissions, completion), flag bloat triggers, obsolete workarounds, verify with 5 scenarios."
metadata:
  hermes:
    tags: [audit, optimization, instruction-debt, astra]
    category: engineering
    phase: audit
    role: auditor
    quality_tier: audit-gated
---

# Instruction Debt Audit

**Propósito:** Auditar la capa de instrucciones de Hermes para detectar "deuda de instrucciones" — reglas que consumen contexto sin valor proporcional.

## Capas a inspeccionar (5 capas)

1. **Descripciones de skills** — triggers amplios, redundancias
2. **Archivos de skills** — lectura obligatoria innecesaria
3. **Definiciones de agentes** — conflictos de autoridad
4. **Permisos** — límites ambiguos o excesivos
5. **Reglas de completado** — paradas prematuras o pendientes abiertos

## Ejecución (solo lectura, propuesta)

### Fase 1: Mapeo del sistema

```bash
# Inventario global
hermes skills list --enabled > inventory.md
hermes config view > config.md
find ~/.local/share/hermes/skills -name "SKILL.md" -exec wc -l {} \; | sort -rn
```

### Fase 2: Análisis por capa

Para cada skill, registrar:
- Ubicación (path)
- Alcance (qué tareas cubre)
- Activación (trigger: always, keyword, intent)
- Peso (líneas de SKILL.md)
- Coste (contexto que carga por defecto)
- Autoridad (precedencia vs otras skills)
- Finalidad (por qué existe)

### Fase 3: Detección de patrones

| Patrón | Qué buscar | Impacto |
|--------|-----------|---------|
| Trigger amplio | Skill se activa con palabras genéricas | Contexto innecesario |
| Lectura obligatoria | SKILL.md cargado en cada interacción | Tokens desperdiciados |
| Workaround heredado | Regla específica para modelo antiguo | Obsolescencia |
| Duplicación | Misma lógica en múltiples skills | Confusión |
| Autoridad vaga | "siempre cargar X" sin criterio | Overhead constante |
| Parada prematura | Regla que corta antes de completar | Errores |

### Fase 4: Stress-test de 5 escenarios

1. **Typo fix** — ¿Activa processes innecesarios?
2. **Database migration** — ¿Mantiene precauciones activas?
3. **UI change** — ¿Selecciona solo capacidades relevantes?
4. **Local test failure** — ¿Distingue fallo nuevo vs preexistente?
5. **Deploy approval** — ¿Respeta límites de autorización?

### Fase 5: Entrega estructurada

Formato de hallazgo:
```markdown
## [Nivel: crítico/alto/medio/bajo] Título
- **Fuente:** archivo:linea o skill:name
- **Problema:** descripción
- **Impacto:** contexto/tokens/pasos adicionales
- **Certeza:** confirmado / hipótesis
- **Propuesta:** diff exacto o texto de reemplazo
- **Salvaguarda:** qué debe preservarse
- **Verificación:** cómo comprobar mejora
```

## Reglas de conducta

- **Solo lectura:** no modificar archivos, solo proponer
- **Evidencia, no autorización:** hallazgos son observaciones, no permiso para actuar
- **Preservar lo intencional:** si algo está ahí deliberadamente, no tocarlo
- **Lote mínimo:** proponer cambios agrupados por archivo, no uno por uno
- **Verificar antes:** cada propuesta debe tener check de cómo validar

## Verificación post-auditoría

Después de aplicar cambios propuestos:
- [ ] Contexto permanente reducido
- [ ] Lecturas obligatorias por tipo de tarea disminuidas
- [ ] Activaciones pertinentes confirmadas
- [ ] Conflictos de autoridad resueltos
- [ ] Estados de finalización más claros
- [ ] Permisos y aprobaciones preservados

## Uso

Ejecutar cuando:
- Se siente que Hermes carga mucho contexto
- Hay lentitud en respuestas
- Skills se activan en momentos incorrectos
- Query: "Audit instruction debt"

No ejecutar cuando:
- El sistema ya está bien scoped (decirlo explícitamente)
- No hay acceso a los archivos del sistema
