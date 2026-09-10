# Pattern Port: idea ajena → scripts propios (verificado 2026-09-03)

Cuándo: un repo NO es instalable (falla en el host, duplica el stack, o es infra),
pero 1-2 patrones de diseño son netos y el usuario dice "porta la idea".

## Recipe (loop-rat → shift_guard + blind_grade)

1. **Leer solo el core, no el harness.** En loop-rat: `bin/lib/guard.py` (245 líneas)
   y la sección grade de `bin/shift`. El resto (schedule, receipts, rat CLI) ya existe
   en Hermes — ignorarlo.
2. **Reescribir limpio para el host**, no copiar: Python stdlib puro, sin
   `signal.SIGPIPE` (no existe en Windows), sin crontab, sin shebang `python3`
   hardcodeado — esas 3 cosas fueron los 91/129 fails del repo original aquí.
   Destino: `$LOCALAPPDATA/hermes/scripts/` (scripts) + config JSON al lado.
3. **Preservar las invariantes del patrón**, que son el valor real:
   - fingerprint `size:mtime` por archivo → el trabajo sucio PREEXISTENTE no se le
     achaqua al turno actual (baseline antes, diff de firmas después).
   - nivel de autonomía desconocido = el MÁS estricto (typo nunca amplía permisos).
   - grader ciego: nunca ve el repo, solo output + diff atribuible + rúbricas;
     un agente que califica su propio turno siempre lo encuentra excelente.
   - verify determinista: exit code de comando, no opinión del modelo.
   - paths del propio harness (state/, receipts) excluidos del conteo — si no,
     todo loop report-only se bloquea solo escribiendo su receipt.
4. **Suite de casos de borde en scratch git repo ANTES de decir "listo"** (7 casos,
   todos ejecutados): limpio / 1 archivo / report-only que escribe → bloqueado /
   denylist (.env) / forma de secreto (sk-ant-…) / blast radius (27>10) / modo diff.
   Y una prueba del grader con backend real (Ollama) emitiendo FAIL con razones
   citadas sobre un turno fake — un grader que solo sabe decir PASS no vale nada.
5. **Enganchar a la skill gobernante** (autonomy-engine: protocolo 4a-4e por tick)
   + registro 4 destinos (§2f del SKILL.md).

## Coste real
~250 líneas de 2 scripts + 3 rúbricas + config, ~20 min con verificación completa.
El harness original eran ~1,350 líneas core + 92 archivos — el ratio patrón/harness
suele ser ~5:1 a favor del port.

## Anti-patrones
- Portar el harness entero "por si acaso" (duplica cron/receipts/CLI nativos).
- Copiar archivos del repo sin leerlos (arrastra sus bugs de plataforma).
- Marcar "portado" sin correr los casos de borde en el host objetivo (regla §22 SOUL).
