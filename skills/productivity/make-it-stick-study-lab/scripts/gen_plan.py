import argparse, os, sys
from datetime import date, timedelta

PLAN = """# Laboratorio de Estudio — 7 días (Make It Stick)

Inicio: {start}
Materias: {topics}

## Método (Make It Stick)
- **Recuperación**: leer NO es estudiar. Cerrar el libro y escribir/decir de memoria.
- **Espaciado**: cada tema se repasa en los días 1, 2, 4 y 7.
- **Intercalado**: mezclar tipos de problemas de días anteriores, no bloques.

## Calendario

| Día | Fecha | Tema nuevo | Repaso espaciado | Técnica |
|-----|-------|-----------|------------------|---------|
{rows}

## Reglas
1. Cada día: 2 oraciones de memoria ANTES de abrir el material.
2. Tarjetas: pregunta al frente, respuesta atrás, fuente citada.
3. Registrar cada fallo en `debilidades.md` (es el mapa de qué practicar).
4. Día 7: consolidar debilidades y decidir el siguiente ciclo.
"""

ROW = "| {d} | {date} | {t} | {r} | {tech} |"
TECHS = ["Recuperación + mapa", "Tarjetas + problemas mixtos", "Práctica intercalada", "Repaso espaciado", "Autoevaluación escrita", "Problemas mixtos", "Consolidación"]

def main():
    ap = argparse.ArgumentParser(description="Genera laboratorio de estudio de 7 días")
    ap.add_argument("carpeta", help="carpeta destino (los PDF/EPUB se dejan intactos)")
    ap.add_argument("--topics", default="tema principal", help="materias separadas por coma")
    ap.add_argument("--start", default=None, help="fecha inicio YYYY-MM-DD (default hoy)")
    a = ap.parse_args()

    start = date.fromisoformat(a.start) if a.start else date.today()
    topics = [t.strip() for t in a.topics.split(",") if t.strip()]

    subdirs = ["tarjetas", "repasos", "notas", "examenes"]
    for s in subdirs:
        os.makedirs(os.path.join(a.carpeta, s), exist_ok=True)

    rows = []
    for i in range(7):
        d = start + timedelta(days=i)
        topic = topics[i % len(topics)]
        repaso = ", ".join(f"D{j+1}" for j in range(i) if i - j in (1, 2, 3, 6))
        rows.append(ROW.format(d=i + 1, date=d.isoformat(), t=topic, r=repaso or "—", tech=TECHS[i]))

    plan = PLAN.format(start=start.isoformat(), topics=", ".join(topics), rows="\n".join(rows))
    with open(os.path.join(a.carpeta, "plan-7-dias.md"), "w", encoding="utf-8") as f:
        f.write(plan)

    # archivos auxiliares si no existen
    for name, header in [
        ("debilidades.md", "# Debilidades (registro de fallos)\n\n| Fecha | Tema | Qué falló | Plan |\n|-------|------|-----------|------|\n"),
        ("mapa-4-cuadros.md", "# Mapa de 4 cuadros\n\n## Qué sé\n\n## Qué NO sé\n\n## Qué practicar\n\n## Qué repasar\n"),
        ("calendario-revision.md", "# Calendario de revisión (espaciado)\n\nD1 → D2 → D4 → D7\n"),
    ]:
        p = os.path.join(a.carpeta, name)
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(header)

    print(f"OK: laboratorio generado en {a.carpeta}")
    print(f"  plan-7-dias.md (inicio {start.isoformat()}, temas: {', '.join(topics)})")
    print(f"  subcarpetas: {', '.join(subdirs)}")
    print("  Originales PDF/EPUB NO se tocan (solo lectura).")

if __name__ == "__main__":
    main()
