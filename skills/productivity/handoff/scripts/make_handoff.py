#!/usr/bin/env python3
"""
make_handoff.py — generador de la estructura de un handoff durable (disciplina ai-memory).

Crea un template markdown en el vault Obsidian con:
  - bloque "> 📍 Where you left off" (el resumen de continuidad para el siguiente agente)
  - frontmatter con type/created/project/next_focus/entities/tags
  - secciones vacías listas para rellenar (Objective/Current State/...)

Uso:
  python make_handoff.py "OBJETIVO_CORTO" --project "F:/Modelos" --next-focus "continuar" \
      --entities "merge,sdxl,vae,fp16" [--vault "C:/Users/<USER>/Documents/Obsidian Vault"]
  (--vault opcional; si se omite usa OBSIDIAN_VAULT_PATH o el default ~/Documents/Obsidian Vault)

Salida: imprime la ruta absoluta del archivo creado (y el bloque "where you left off")
        para que la skill lo reporte al usuario.
"""
import argparse
import datetime
import os
import re
import sys

DEFAULT_VAULT = os.path.join(os.path.expanduser("~"), "Documents", "Obsidian Vault")
HANDOFF_DIR_SUBPATH = os.path.join("Memorias", "Handoffs")


def _resolve_vault(explicit: str) -> str:
    if explicit:
        return explicit
    env = os.environ.get("OBSIDIAN_VAULT_PATH")
    if env and os.path.isdir(env):
        return env
    return DEFAULT_VAULT


def _slug(text: str) -> str:
    """Convierte objetivo en un slug corto para el nombre de archivo."""
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return s[:40] or "handoff"


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera un template de handoff durable.")
    ap.add_argument("objective", help="Objetivo corto de la sesion (sirve para el slug y el titulo)")
    ap.add_argument("--vault", default=None, help="Ruta al vault Obsidian")
    ap.add_argument("--project", default=None, help="Nombre del proyecto (basename(cwd) por defecto)")
    ap.add_argument("--next-focus", default="continue", help="Foco de la siguiente sesion")
    ap.add_argument("--entities", default="", help="Lista separada por comas de sustantivos clave")
    args = ap.parse_args()

    vault = _resolve_vault(args.vault)
    handoff_dir = os.path.join(vault, HANDOFF_DIR_SUBPATH)
    os.makedirs(handoff_dir, exist_ok=True)

    now = datetime.datetime.now().astimezone()
    ts = now.strftime("%Y-%m-%d_%H%M%S")
    iso = now.isoformat()
    slug = _slug(args.objective)

    project = args.project or os.path.basename(os.getcwd()) or "default"
    entities = [e.strip() for e in args.entities.split(",") if e.strip()][:10]

    # Entidades → YAML list (comillas para strings con espacio)
    entities_yaml = "[" + ", ".join(f'"{e}"' for e in entities) + "]" if entities else "[]"
    # usa el slug en vez de arg para el archivo
    _ = slug

    # Bloque "where you left off" — lo inyecta el siguiente agente como contexto
    where_block = (
        "> \U0001f4cd **Where you left off:** \n"
        f"> Continuar desde: `handoff-{ts}.md` | Proyecto: `{project}` | Última acción: (verificar)\n"
    )

    content = (
        f"{where_block}\n"
        "---\n"
        "type: handoff\n"
        f"created: {iso}\n"
        f"project: {project!r}\n"
        f"next_focus: {args.next_focus!r}\n"
        f"entities: {entities_yaml}\n"
        "tags: [handoff, " + project.replace(" ", "-") + "]\n"
        'source: "conversation"\n'
        "---\n\n"
        f"# Handoff — {args.objective}\n"
        f"*Generated: {iso} | Next focus: {args.next_focus}*\n\n"
        "## Objective\n- \n\n"
        "## Current State\n- [ ] Done: \n- [ ] In progress: \n- [ ] Next: \n\n"
        "## Key Decisions\n- \n\n"
        "## Files Touched\n- \n\n"
        "## Suggested Skills for Next Agent\n- \n\n"
        "## Context Pointers\n- \n\n"
        "## Open Questions\n- \n"
    )

    filename = f"handoff-{ts}.md"
    path = os.path.join(handoff_dir, filename)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    readable_path = path.replace(os.sep, "/")
    print(f"HANDOFF_CREATED {readable_path}")
    print(
        f"> \U0001f4cd **Where you left off:** ({args.objective}) — rellena el resto en el archivo."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
