"""Plantilla de parity test: Rust vs Python para un hot path aislado.
Prueba que la funcion Rust es IDENTICA a la Python que reemplaza, en casos
borde + fuzz, y reporta speedup. Exit 0 = parity garantizada; exit 1 = NO ships.
USO: ajustar IMPORT_RUST, RUST_FN, PY_FN y CASES.
"""
import sys, random, time

try:
    import fuzzy_norm_rs as rust  # <-- cambiar por tu modulo
except Exception as e:
    print(f"FAIL import rust: {e}"); sys.exit(2)

# Funciones a comparar (cambiar firmas segun tu caso)
def rust_fn(c): return rust.stripped_lines(c)
def py_fn(c):   return [line.strip() for line in c.split('\n')]

CASES = [
    "", "\n", "  \n\t\n", "def foo():\n    pass\n",
    "  def foo():  \n\tpass\n", "a   b\t\t c\n  d",
    "no_newline_at_end", "\n\n\n", "    \n\t\t\n   x   y  \t z\n",
    "  héllo  world  \n\tña\n", "Mixed\tTabs and   Spaces\nhere\n",
]
random.seed(1234)
for _ in range(2000):
    CASES.append("".join(random.choice([" ", "\t", "a", "b", "(", ")", ":", "\n", "x"])
                          for _ in range(random.randint(0, 40))))
# caso caliente real
lines = []
for i in range(3000):
    ind = "    " * (i % 5)
    lines.append(f"{ind}def f_{i}(x):"); lines.append(f"{ind}    return {i}")
CASES.append("\n".join(lines))

fails = 0
for idx, c in enumerate(CASES):
    if rust_fn(c) != py_fn(c):
        print(f"[FAIL] case#{idx}: rust={rust_fn(c)!r} py={py_fn(c)!r}")
        fails += 1
        if fails > 5: break
if fails:
    print(f"PARITY FAILED: {fails}"); sys.exit(1)

big = CASES[-1]
t0 = time.perf_counter()
for _ in range(300): py_fn(big)
py_ms = (time.perf_counter()-t0)/300*1000
t0 = time.perf_counter()
for _ in range(300): rust_fn(big)
rs_ms = (time.perf_counter()-t0)/300*1000
print(f"PARITY OK ({len(CASES)} cases) | python={py_ms:.3f}ms rust={rs_ms:.3f}ms speedup={py_ms/rs_ms:.2f}x")
sys.exit(0)
