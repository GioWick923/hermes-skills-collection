# Template: Matriz de Cruce Social-Experto

## Cómo usar esta matriz

Por cada hallazgo social, generar una entrada. Luego buscar la contraparte
experta y llenar la columna correspondiente. El veredicto se determina
comparando ambas columnas.

## Matriz vacía (copiar y llenar)

| # | Hallazgo Social | Fuentes Sociales | Recencia | Contraparte Experta | Fuentes Expertas | Veredicto | Notas |
|---|---|---|---|---|---|---|---|
| 1 | "La gente dice X..." | Reddit (3 threads), HN (1 post) | 2026-Q2 | "El experto dice Y..." | Docs oficiales, GitHub issue #123 | ✅ Confirma | ... |
| 2 | ... | ... | ... | ... | ... | ⚠️ Matiza | ... |
| 3 | ... | ... | ... | ... | ... | ❌ Corrige | ... |
| 4 | ... | ... | ... | ... | ... | 💎 Revela | ... |
| 5 | ... | ... | ... | ... | ... | 🔄 Evoluciona | ... |
| 6 | ... | ... | ... | ... | ... | ❓ Inconcluso | ... |

## Códigos de Veredicto

| Código | Significado | Cuándo usarlo |
|---|---|---|
| ✅ CONFIRMA | Comunidad y expertos coinciden | La claim social es respaldada por evidencia técnica |
| ⚠️ MATIZA | Comunidad tiene razón parcial | El experto añade contexto que cambia la interpretación |
| ❌ CORRIGE | Comunidad se equivoca | El experto desmiente con evidencia sólida |
| 💎 REVELA | Comunidad sabe más que docs | Sabiduría callejera confirmada, docs no mencionan esto |
| 🔄 EVOLUCIONA | Info social está desactualizada | La situación cambió, la opinión social es de versión antigua |
| ❓ INCONCLUSO | No hay suficiente evidencia | Ni comunidad ni expertos dan respuesta clara |

## Ejemplo completo (referencia)

| # | Hallazgo Social | Fuentes Sociales | Recencia | Contraparte Experta | Fuentes Expertas | Veredicto |
|---|---|---|---|---|---|---|
| 1 | "Bun.js es 10x más rápido que Node" | Reddit r/javascript (5 threads), HN (3 debates), X (multiples) | 2026-Q1 | "Bun es más rápido en benchmarks específicos pero no 10x en producción real" | Bun benchmarks repo, Deno blog comparison, Engineering post by K. Kelly | ⚠️ Matiza |
| 2 | "Bun tiene memory leaks en producción" | Reddit (2 threads con +500 upvotes), GitHub issues | 2026-Q2 | "Confirmado: issue #1234, memory leak en HTTP server con keep-alive" | GitHub issue #1234 (open), Bun changelog v1.1.13 | ✅ Confirma |
| 3 | "Bun reemplaza Node completamente" | Reddit (opinión dividida), X (hype) | 2026-Q1 | "Bun no soporta todas las APIs de Node todavía, compatibilidad ~90%" | Node compat docs de Bun, Bun roadmap | ❌ Corrige |
| 4 | "Usa `bun --bun` flag para mejor performance" | Reddit r/Bun (1 post con trucos) | 2026-Q2 | "No documentado formalmente pero confirmado por maintainer en Discord" | Discord message from Jarred-Sumner, changelog mention | 💎 Revela |
