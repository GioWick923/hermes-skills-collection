# TEMA-CORTO (ej. hermes-git-backup)

- Qué: una frase sobre qué cubre la nota.
- Cuándo/por qué: contexto que hizo que lo aprendieras (sesión, problema, fuente).
- Cómo: pasos o comandos clave, mínimo pero reproducible.
- Fuente: de dónde vino (skill, Reddit r/HermesAgent, docs oficiales, propio).
- Pitfalls: errores reales que costaron tiempo, para no repetirlos.

## Reglas del zettel
- Nombre de archivo: `AAAA-MM-DD-tema.md` dentro de `second-brain/zettel/`.
- Una idea/noción por nota; enlaza con otras si hace falta.
- NUNCA incluyas secretos (tokens, api keys, passwords).
- Si la nota se vuelve preferencia/identidad duradera del usuario, promuévela a
  `memories/MEMORY.md` y bórrala de aquí.
- Añade una línea al `second-brain/README.md` índice.

## Ejemplo mínimo
# hermes-git-backup
- Qué: versionar config de Hermes con git excluyendo secretos.
- Cómo: `git init` en `$LOCALAPPDATA/hermes`; `.gitignore` excluye .env/auth.json/
  config.yaml/*.db/tools//sessions//**/.git/; `git add .`; `backup-state.sh` para secretos.
- Pitfalls: `git add -A` → mmap failed en MSYS; usar `git add .`.
