use pyo3::prelude::*;

/// Drop-in replacement. Iterate `char`s (not bytes) to keep UTF-8 intact.
#[pyfunction]
fn strip_ansi(text: &str) -> String {
    // Fast path: bail if no ESC and no 8-bit C1 byte.
    let has_escape = text.bytes().any(|b| b == 0x1B || (0x80..=0x9F).contains(&b));
    if !has_escape {
        return text.to_string();
    }
    let chars: Vec<char> = text.chars().collect();
    let n = chars.len();
    let mut out: Vec<char> = Vec::with_capacity(n);
    let mut i = 0;
    while i < n {
        let c = chars[i];
        // 8-bit C1 controls: \u{9b}=8-bit CSI, \u{9d}=8-bit OSC, others dropped.
        if (0x80u32..=0x9Fu32).contains(&(c as u32)) {
            match c as u32 {
                0x9B => { i += 1; while i < n { let d = chars[i] as u32;
                    if (0x30..=0x3F).contains(&d) || (0x20..=0x2F).contains(&d) { i += 1; }
                    else if (0x40..=0x7E).contains(&d) { i += 1; break; } else { break; } }
                    continue; }
                0x9D => { i += 1; while i < n { let d = chars[i] as u32;
                    if d == 0x07 || d == 0x9C { i += 1; break; } else { i += 1; } }
                    continue; }
                _ => { i += 1; continue; }
            }
        }
        // ESC-initiated sequences (0x1B)
        if c as u32 == 0x1B {
            if i + 1 < n {
                let next = chars[i + 1]; let nx = next as u32;
                match next {
                    '[' => { i += 2; while i < n { let d = chars[i] as u32;
                        if (0x30..=0x3F).contains(&d) || (0x20..=0x2F).contains(&d) { i += 1; }
                        else if (0x40..=0x7E).contains(&d) { i += 1; break; } else { break; } }
                        continue; }
                    ']' => { i += 2; while i < n { let d = chars[i];
                        if d as u32 == 0x07 { i += 1; break; }
                        else if d as u32 == 0x1B && i+1 < n && chars[i+1] == '\\' { i += 2; break; }
                        else { i += 1; } } continue; }
                    'P' | 'X' | '^' | '_' => { i += 2; while i < n { let d = chars[i];
                        if d as u32 == 0x1B && i+1 < n && chars[i+1] == '\\' { i += 2; break; }
                        else { i += 1; } } continue; }
                    _ if (0x20..=0x2F).contains(&nx) => { i += 2; while i < n { let d = chars[i] as u32;
                        if (0x30..=0x7E).contains(&d) { i += 1; break; } else { i += 1; } } continue; }
                    _ if (0x30..=0x7E).contains(&nx) => { i += 2; continue; }
                    _ => { out.push(c); i += 1; continue; }  // keep lone/unknown ESC
                }
            } else { out.push(c); i += 1; continue; }  // lone ESC at end: keep
        }
        out.push(c); i += 1;
    }
    out.iter().collect()
}

#[pymodule]
fn ansi_strip_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(strip_ansi, m)?)?;
    Ok(())
}
