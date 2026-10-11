#!/usr/bin/env python3
"""Verificador estructural de Pine Script (TradingView) — sin compilador local.

Uso:
  python verify_pine.py <archivo.pine> [--residual "Turco1 Turco2 ..."]

Chequeos:
  1. Tokens del idioma original que quedaron en el código (pasados con --residual)
  2. Toda comparación == "..." debe referenciar una opción/valor definido
  3. Balance de paréntesis fuera de strings
  4. Conteo de líneas y bytes
Salida: VEREDICTO OK / REVISAR. Exit code 0 = OK, 1 = revisar, 2 = uso incorrecto.
"""
import re
import sys


def main():
    args = sys.argv[1:]
    if not args:
        print('Uso: python verify_pine.py <archivo.pine> [--residual "T1 T2"]')
        sys.exit(2)
    path = args[0]
    residual = []
    if "--residual" in args:
        i = args.index("--residual")
        residual = args[i + 1].split() if i + 1 < len(args) else []
    src = open(path, encoding="utf-8").read()

    # 1. Tokens residuales del idioma original
    found = {t: src.count(t) for t in residual if src.count(t) > 0}
    print("1) RESIDUAL:", found if found else "NINGUNO OK")

    # 2. Opciones definidas vs comparaciones == "..."
    opts = set(re.findall(r"options=\[(.*?)\]", src, re.S))
    known = set()
    for o in opts:
        for m in re.findall(r'"([^"]+)"', o):
            known.add(m)
    # valores fijos que suelen compararse sin estar en options=
    known |= {"EMA", "SMA", "HMA", "Solid", "Dashed", "Dotted",
              "Tiny", "Small", "Normal", "Large",
              "1", "3", "5", "15", "30", "45", "60", "120", "180", "240", "D", "W", "M"}
    comps = set(re.findall(r'== "([^"]+)"', src)) | set(re.findall(r"== '([^']+)'", src))
    missing = {c for c in comps if c not in known}
    print("2) COMPARACIONES sin opción:", sorted(missing) if missing else "NINGUNA OK")

    # 3. Balance de paréntesis (fuera de strings)
    nop = re.sub(r'"[^"]*"', '""', src)
    nop = re.sub(r"'[^']*'", "''", nop)
    bal = nop.count("(") - nop.count(")")
    print("3) PAREN balance:", bal, "(0 = OK)" if bal == 0 else "(REVISAR)")

    # 4. Líneas y tamaño
    print("4) LINEAS:", src.count(chr(10)) + 1, "| bytes:", len(src.encode("utf-8")))

    ok = not found and not missing and bal == 0
    print("VEREDICTO:", "OK OK" if ok else "REVISAR (atencion)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
