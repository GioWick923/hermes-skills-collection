---
name: python-hotpath-to-rust
description: Acelera hot paths de Python en Rust SIN romper nada. Usar cuando un módulo Python de Hermes (o propio) tenga un cuello de botella aislable (loops sobre strings/listas, strip/trim, parsing, normalización, collapse de whitespace) y se quiera ganar velocidad compilando un .pyd con pyo3, manteniendo SIEMPRE fallback a Python puro y parity tests obligatorios. Aplica solo a funciones PURAS y pequeñas; NUNCA portar lógica de matching/difflib/mapeo de posiciones completa de golpe. El agente debe aplicar este flujo proactivamente en el futuro cada vez que detecte un hot path candidato en código Python que mantiene.
---

# Python Hot-Path → Rust (seguro, con fallback y parity)

Estrategia híbrida: dejas el 90% en Python y solo aceleras el núcleo puro y
aislable en Rust, expuesto como módulo `.pyd` vía pyo3. La clave de seguridad es
que **el comportamiento es idéntico** al path Python (probado) y que **si el
`.pyd` falta, cae al path Python** automáticamente.

## Cuándo SÍ usar
- Hot path medido (no asumido): loop sobre miles de líneas/caracteres por llamada.
- Función PURA y pequeña: `strip` línea-por-línea, `re.sub` simple, split/parse,
  collapse de whitespace, normalización barata, conteo.
- El llamador hace el matching/mapeo de posiciones (Rust solo preprocesa).

## Cuándo NO usar (riesgo alto, ROI dudoso)
- Lógica de matching completa (cadenas de estrategias, `difflib.SequenceMatcher`).
- Mapeo de posiciones best-effort/frágil (ej. `_map_normalized_positions`).
- Módulos sin tests de paridad donde un fallo corrompa estado del usuario
  (edición de archivos, credenciales, DB) y no puedas aislar la función pura.
- I/O-bound (red/disco): Rust no es más rápido que Python ahí.

## Prerrequisitos (Windows, entorno ya verificado en esta máquina)
- `cargo` 1.97+ y `rustc` (estable x86_64-pc-windows-msvc).
- MSVC BuildTools 2022: `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat x64`.
- `python311.lib` en `%USERPROFILE%\..\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\libs\` (usado por pyo3).
- Cache de registry de cargo poblado (`%USERPROFILE%\.cargo\registry\cache\index.crates.io-...`) → compila **offline**. No hace falta maturin.
- `rustfmt.exe` puede faltar: es solo warning del linter, NO error de compilación.

## Flujo de 7 pasos (loop cerrado, verificar antes de declarar hecho)

### Paso 0 — Perfilar para encontrar el cuello REAL
No asumas. Mide cada estrategia/camino con `time.perf_counter()` sobre un caso
grande (ej. 6000 líneas). El cuello suele ser un `split('\n')`+`.strip()` por
línea o un `re.sub` sobre todo el archivo en cada llamada, no la lógica cara rara.

### Paso 1 — Aislar la función pura y copiar su semántica EXACTA
Lee el código Python original. Tu Rust debe replicar byte-a-byte:
- `[line.strip() for line in content.split('\n')]` → `content.split('\n')` conserva
  entrada vacía final si termina en `\n`; `str.strip()` quita whitespace Unicode.
- `re.sub(r'[ \t]+', ' ', s)` → colapsa runs de SPACE/TAB a un espacio, deja `\n`.

### Paso 2 — Crear el crate (pyo3 cdylib)
Ver plantilla en `references/minimal_lib.rs` y `references/build_windows.bat`.
```toml
[lib]
name = "tu_modulo_rs"
crate-type = ["cdylib"]
[dependencies]
pyo3 = { version = "0.23", features = ["extension-module"] }
```
NOTA pyo3 0.23: `PyList::new_bound` está deprecado → usa `PyList::new`; 
`into_py` deprecado → usa `into_pyobject(py)?.into_any().unbind()`. Son warnings, compila.

### Paso 3 — Compilar offline e instalar como .pyd
```bat
set CARGO_NET_OFFLINE=true
set PYO3_PYTHON=%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe
set PYTHON_SYS_EXECUTABLE=%PYO3_PYTHON%
cargo build --release
copy target\release\tu_modulo_rs.dll target\release\tu_modulo_rs.pyd
:: instalar en site-packages del venv
```
RUITA MSYS: escribir rutas como `C:\ruta` (no `/c/ruta`) para evitar que el
resolver cree duplicados en `C:\c\...`. Si pasa, borrar el duplicado.

### Paso 4 — Parity test Rust vs Python (OBLIGATORIO)
Usa `templates/parity_test.py`: fuzz + casos borde (vacío, solo `\n`, tabs,
UTF-8, trailing newline, 6000 líneas). Debe dar `PARITY OK` con exit 0 y
mostrar speedup. Si diverge → NO ships.

### Paso 5 — Cablear en Python con fallback seguro
```python
try:
    import tu_modulo_rs as _rs
    _HAS_RUST = True
except Exception:
    _rs = None
    _HAS_RUST = False

def _stripped_lines(content):
    if _HAS_RUST:
        return list(_rs.stripped_lines(content))
    return [line.strip() for line in content.split('\n')]
```
El llamador (matching/mapeo de posiciones) queda IGUAL en Python → paridad de
comportamiento por construcción.

### Paso 6 — Behavior parity del módulo completo (ON vs OFF)
Desactiva `_HAS_RUST` y compara `fuzzy_find_and_replace(...)` (o la función
pública) sobre 3000+ casos fuzz. 0 divergencias o no ships.

### Paso 7 — Dejar instalado + cleanup
`.pyd` en site-packages del venv. Borrar directorio duplicado fantasma si el
resolver MSYS lo creó. No tocar el código Python que no se usa.

## Pitfalls (aprendidos de la implementación real)
- MSYS resuelve `/c/foo` → `C:\c\foo` (fuera del workspace): usa `C:\foo`.
- `rustfmt` ausente = warning del linter, no bloquea compilación.
- pyo3 0.23 renombres (`PyList::new`, `into_pyobject`) = warnings, compila.
- NO mapees byte offsets de Rust a Python para UTF-8 tú mismo si puedes evitarlo;
  devuelve solo las líneas normalizadas y deja que Python calcule posiciones con
  `content.split('\n')` original.
- Nunca portes `difflib.SequenceMatcher` ni mapeo best-effort a Rust sin tests.

## Verification checklist (no declarar hecho sin esto)
- [ ] `parity_test.py` → `PARITY OK`, exit 0, speedup >1x.
- [ ] Import del módulo Python → Rust activo (`_HAS_RUST is True`).
- [ ] E2E: caso real de la función pública da resultado correcto.
- [ ] Behavior parity (ON vs OFF) 3000+ casos → 0 divergencias, exit 0.
- [ ] `.pyd` instalado en site-packages; fallback a Python verificado desactivando `_HAS_RUST`.

## Referencias
- `references/minimal_lib.rs` — esqueleto pyo3 con `stripped_lines` + `collapse_ws`.
- `references/build_windows.bat` — build offline + install en venv Hermes.
- `templates/parity_test.py` — plantilla de parity test (fuzz + edge + speed).

## Ejemplo real ya entregado
`tools/fuzzy_match.py` estrategia 2 (`line_trimmed`): usó `_stripped_lines` Rust
(crate `fuzzy_norm_rs`). Paridad 100% en 3003+ casos, 2x speedup, fallback seguro.
