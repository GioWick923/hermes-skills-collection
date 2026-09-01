# Electronic Circuit Diagrams — SVG Pattern for HTML Deliverables

When the deliverable is an electronic circuit schematic (inverter, amplifier, power supply, motor driver, Arduino wiring), the base `architecture-diagram` skill's cloud/software aesthetic doesn't fully apply. This reference captures the adaptations that worked in a real session (SG3525 1000W inverter diagram).

## SVG structure for circuits

### ViewBox

Use a wide viewBox to fit the circuit horizontally (IC on left-center, MOSFETs mid-right, transformer on right, battery bottom-left):

```svg
<svg viewBox="0 0 1240 900" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="13">
```

### Color semantics for electronic circuits

| Color | Hex | Used for |
|---|---|---|
| Red | `#ff6b6b` | +V power rail, fuse, high voltage warning |
| Amber | `#ffd166` | IC body, gate drive signals, labels |
| Orange | `#ff9f43` | MOSFET symbols, drain/source/gate |
| Blue | `#4ea1ff` | Signal/control, transformer secondary, output |
| Gray | `#9db8d9` | GND, passive components |
| Dark bg | `#0f1420` | Page background |
| Panel bg | `#1a2740` | IC body fill |

### Component rendering patterns

**IC (e.g., SG3525):** Rounded rect with pin labels on both sides. Left pins = inputs/timing; right pins = outputs/reference/power.

```svg
<g transform="translate(250,180)">
  <rect x="0" y="0" width="150" height="360" rx="6" fill="#1a2740" stroke="#ffd166" stroke-width="2.5"/>
  <text x="75" y="24" text-anchor="middle" fill="#ffd166" font-size="15" font-weight="bold">SG3525</text>
  <!-- pin labels left -->
  <text x="-4" y="70" text-anchor="end" fill="#cfd8ea">PIN 1  IN− (realim.)</text>
  <!-- pin stubs -->
  <line x1="0" y1="64" x2="-14" y2="64" stroke="#4ea1ff" stroke-width="2"/>
  ...
</g>
```

**MOSFET (simplified symbol):** Gate (left stub) → body rect → drain (top) / source (bottom).

```svg
<g transform="translate(700,330)">
  <line x1="20" y1="0" x2="20" y2="60" stroke="#ff9f43" stroke-width="3"/> <!-- gate stub -->
  <line x1="0" y1="30" x2="40" y2="30" stroke="#ff9f43" stroke-width="3"/> <!-- gate -->
  <rect x="22" y="95" width="16" height="30" fill="none" stroke="#ff9f43" stroke-width="2"/> <!-- body -->
  <text x="30" y="143" text-anchor="middle" fill="#ff9f43" font-size="11">Q1 IRF3205</text>
  <line x1="30" y1="60" x2="30" y2="95" stroke="#ff9f43" stroke-width="3"/> <!-- drain line up -->
  <line x1="30" y1="125" x2="30" y2="160" stroke="#ff9f43" stroke-width="3"/> <!-- source line down -->
</g>
```

**Transformer:** Rect with interior núcleo, primario on one side, secundario on the other.

```svg
<g transform="translate(980,120)">
  <rect x="0" y="120" width="120" height="360" rx="8" fill="#1c2a44" stroke="#4ea1ff" stroke-width="2"/>
  <rect x="30" y="150" width="60" height="300" fill="#2c3e60" stroke="#4ea1ff" stroke-width="1"/>
  <text x="60" y="295" text-anchor="middle" fill="#4ea1ff" font-size="13" font-weight="bold">T1 12-0-12V</text>
  <!-- primario leads -->
  <line x1="0" y1="160" x2="30" y2="160" stroke="#ff9f43" stroke-width="3"/>
  <line x1="90" y1="160" x2="120" y2="160" stroke="#ff9f43" stroke-width="3"/>
  <!-- secundario leads -->
  <line x1="0" y1="440" x2="30" y2="440" stroke="#4ea1ff" stroke-width="3"/>
  <line x1="90" y1="440" x2="120" y2="440" stroke="#4ea1ff" stroke-width="3"/>
</g>
```

**Battery + fuse:** Battery rect with + terminal; fuse rect in the +12V rail.

## BOM table pattern (two-column for density)

```html
<div class="fila"><div class="col">
<table>
<tr><th>Cant.</th><th>Componente</th><th>Referencia</th></tr>
<tr><td>4</td><td>MOSFET IRF3205</td><td>Q1–Q4</td></tr>
</table>
</div><div class="col">
<table>...</table>
</div></div>
```

## Pinout table pattern

One row per IC pin: Pin → Function → Connect-to.

```html
<table>
<tr><th>Pin</th><th>Función</th><th>Conectar a</th></tr>
<tr><td>11</td><td>Salida A</td><td>→ Rg1 10Ω → gates Q1+Q2 (rama A)</td></tr>
<tr><td>7</td><td>RD (dead-time)</td><td>470Ω entre pin5 y pin7 — clave anti-calor</td></tr>
</table>
```

## Safety warning block (mandatory for HV/HC circuits)

```html
<div class="warn"><strong>⚠️ SEGURIDAD:</strong> la salida es 120/220V real —
<strong>peligro de muerte</strong> por contacto. A 12V y 1000W circulan
<strong>≈83 A</strong>: cable de 10 mm² o más, fusible obligatorio,
y nunca operar sin disipador bien fijado.</div>
```

## SVG verification by DOM (when browser_vision fails)

`browser_vision` can fail if the active model lacks vision (e.g., `deepseek-v4-flash`) or the vision endpoint is saturated. DOM verification is a reliable fallback — it checks the SVG is in the rendered DOM with its labels and at the expected size.

```javascript
// browser_console expression to verify SVG integrity
(() => {
  const s = document.querySelector('svg');
  if(!s) return JSON.stringify({hasSvg:false, svgCount: document.querySelectorAll('svg').length});
  const r = s.getBoundingClientRect();
  const texts = s.querySelectorAll('text').length;
  let overflow = [];
  s.querySelectorAll('*').forEach(el => {
    try {
      const bb = el.getBBox();
      if (bb && (bb.x + bb.width > 1240 || bb.y + bb.height > 900 || bb.x < 0))
        overflow.push((el.textContent || el.tagName).slice(0, 30));
    } catch(e) {}
  });
  return JSON.stringify({
    hasSvg: true,
    svgW: Math.round(r.width),
    svgH: Math.round(r.height),
    textElements: texts,
    overflow: overflow.slice(0, 40),
    viewBox: s.getAttribute('viewBox')
  });
})()
```

### Interpretation

- `hasSvg: true` + `textElements > 0` → SVG is in the DOM with labels — good.
- `svgW/svgH` within the viewBox dimensions → rendered at expected size.
- `overflow` entries are often **false positives** from elements inside `<g transform="...">` groups — their `getBBox()` returns coordinates in the group's local space. If the text count matches expected labels (Q1-Q4, T1, IC name, pin numbers, voltage values), the diagram is fine.
- If `hasSvg: false` after `browser_navigate`, the browser may have reset to `about:blank` — re-navigate to the file URL before running the console check.

### Label presence check (optional, deeper)

```javascript
(() => {
  const svg = document.querySelector('svg');
  const ids = ['Q1','Q2','Q3','Q4','T1','SG3525','IRF3205','220V','PIN'].map(w => {
    let n = 0;
    svg.querySelectorAll('text').forEach(t => { if(t.textContent.includes(w)) n++; });
    return w + ':' + n;
  });
  return JSON.stringify(ids);
})()
```

If key component labels return `:0`, they're missing from the SVG — check the source.

## Pitfalls specific to circuit diagrams

- **Z-order of connections vs components:** draw connection lines BEFORE component rects so they render behind the boxes (same as architecture-diagram base skill, but extra important for circuits where lines represent physical wires that shouldn't visually cross over component labels).
- **Pin label readability:** pin labels on ICs are small (11-13px). Use `text-anchor="end"` for left-side labels and left-align for right-side to keep them readable near the pin stubs.
- **Transformer tap labeling:** clearly mark center tap (0V) vs outer ends (12V) — this is where users wire incorrectly. A label like "+12V → centro (tap) del primario 12-0-12" prevents wiring mistakes.
- **Dead-time resistor:** if the circuit relies on dead-time (SG3525 RD pin 7), make it visually prominent in the SVG and in the pinout table — it's the #1 anti-heating component and the user needs to know it's not optional.
