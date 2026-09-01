# Agency — Equipo multiagente (Agency Agents → Hermes)

Pack de 7 skills traducidos/adaptados del repo [msitarzewski/agency-agents]
(147 agentes open-source). Todos llevan `category: agency` para filtrar con
`skills_list(category='agency')`. El orquestador delega en los demás vía
`delegate_task` (resuelve por `name`, no por ruta → mover carpetas es seguro).

## Índice

| Skill | Carga con | Rol |
|-------|-----------|-----|
| `agency-orchestrator` | `skill_view(name='agency-orchestrator')` | Conductor del pipeline: plan → [dev↔QA] → reality check |
| `agency-architect` | `agency-architect` | ADRs, DDD, patrones, trade-offs |
| `agency-backend-architect` | `agency-backend-architect` | Backend escalable, APIs, confiabilidad, observabilidad |
| `agency-ai-engineer` | `agency-ai-engineer` | ML/LLM a producción, RAG, MLOps, ética |
| `agency-senior-developer` | `agency-senior-developer` | Implementación full-stack de calidad |
| `agency-test-automation` | `agency-test-automation` | E2E determinista, anti-flake |
| `agency-reality-checker` | `agency-reality-checker` | Certificación escéptica basada en evidencia |

## Cómo usar

1. El usuario pide "construye X con el equipo Agency".
2. Cargo `agency-orchestrator`.
3. Este delega por fase usando `delegate_task` con `toolsets` acotados:
   - arquitectura/backend → `['terminal','file','web']`
   - QA visual → añade `['browser']`
4. Cada fase es un subagente aislado con entregable verificable (cierre de loop).

## Convenciones de este pack

- `name` siempre con prefijo `agency-`.
- `category: agency` para filtrado.
- Lenguaje: español.
- Referencias entre skills: por `name` (no por ruta).
