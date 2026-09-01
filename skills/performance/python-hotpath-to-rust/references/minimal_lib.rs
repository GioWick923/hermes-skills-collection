//! Plantilla mínima pyo3 (cdylib) para acelerar un hot path puro de Python.
//! Semántica: replicar EXACTAMENTE la función Python que reemplaza.
//! Solo código PURo y pequeño. Ver skill python-hotpath-to-rust.

use pyo3::prelude::*;
use pyo3::types::PyList;

/// Equivale a `[line.strip() for line in content.split('\n')]`.
/// `split('\n')` conserva entrada vacía final si el string termina en '\n'.
/// `str::trim()` quita whitespace Unicode, igual que Python `str.strip()`.
#[pyfunction]
fn stripped_lines(py: Python, content: &str) -> PyResult<Py<PyList>> {
    let mut out: Vec<PyObject> = Vec::with_capacity(content.len() / 40 + 1);
    for raw in content.split('\n') {
        out.push(raw.trim().into_pyobject(py)?.into_any().unbind());
    }
    Ok(PyList::new(py, out).unbind())
}

/// Equivale a `re.sub(r'[ \t]+', ' ', s)`:
/// colapsa runs de SPACE/TAB a un espacio, deja '\n' y demás intactos.
#[pyfunction]
fn collapse_ws(_py: Python, s: &str) -> PyResult<String> {
    let mut out = String::with_capacity(s.len());
    let mut in_ws = false;
    for ch in s.chars() {
        if ch == ' ' || ch == '\t' {
            if !in_ws {
                out.push(' ');
                in_ws = true;
            }
        } else {
            out.push(ch);
            in_ws = false;
        }
    }
    Ok(out)
}

#[pymodule]
fn tu_modulo_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(stripped_lines, m)?)?;
    m.add_function(wrap_pyfunction!(collapse_ws, m)?)?;
    Ok(())
}
