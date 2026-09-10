# Trading Dashboard (QuantDesk) — arquitectura, servidor ejecutor y auditoría

> Patrón verificado 2026-09-01. Cómo exponer el pipeline TimesFM-3 + Perfil de Volumen
> como una plataforma web en vivo, y cómo auditar el stack completo antes de entregar.

## Arquitectura (3 piezas)
1. **`pipeline_forecast_flow.py`** — corre el modelo + perfil y escribe `pipeline_output.json`.
2. **`run_server.py`** — `ThreadingHTTPServer` que SIRVE los estáticos Y expone un endpoint
   `/api/run` que re-ejecuta el pipeline por `subprocess` y refresca los JSON. Frontend hace
   `fetch('pipeline_output.json')` al cargar y `fetch('/api/run')` al pulsar "Ejecutar".
3. **`index.html`** — dashboard ECharts + micro-animaciones CSS/JS.

### Servidor ejecutor (la pieza clave para "botón que regenera datos reales")
```python
class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=QUANT, **kw)   # sirve estáticos de la carpeta
    def do_GET(self):
        if self.path == "/api/run":
            # subprocess del pipeline real; timeout 600; copia JSONs a la carpeta servida
            r = subprocess.run([PYTHON, PIPELINE], cwd=ORCH, capture_output=True, text=True, timeout=600)
            self._send_json({"ok": r.returncode == 0, ...})
        else:
            super().do_GET()   # SimpleHTTPRequestHandler sirve index.html + JSONs
```
- El venv del pipeline debe ser RUTA ABSOLUTA (no confiar en PATH del servidor).
- Copiar los JSON de salida a la carpeta que el frontend lee (para que `fetch` los vea).

### Frontend: datos reales, no demo
```js
async function loadPipelineData(){ // fetch del JSON al boot
  const r = await fetch('pipeline_output.json', {cache:'no-store'});
  PIPELINE_DATA = await r.json();
}
// botón Ejecutar -> /api/run -> recarga JSON -> re-render de secciones IA/mercado
```

## Patrón de micro-animaciones (UI premium, verificado)
- **Solo `transform`/`opacity`** en transiciones (60fps). NUNCA `transition:all` (un auditor lo
  marca). Cambiar `transition:all` a propiedades explícitas (`transform,box-shadow,border-color,...`).
- **Tokens de motion** en `:root`: `--ease-out:cubic-bezier(.16,1,.3,1)` (deceleration, llegar),
  `--ease-in:cubic-bezier(.7,0,.84,0)` (salir), `--spring:cubic-bezier(.34,1.56,.64,1)` (overshoot).
- **Exit más rápido que enter** (70% de la duración de entrada).
- **Stagger** de entrada ~40ms por item (`nth-child(n)` delays).
- Botones: push `:active{transform:scale(.96)}`, glow en hover, icono rota/crece al hover.
- **`prefers-reduced-motion`**: media query que reduce TODO a `.01ms` — obligatorio.
- **Count-up** de números con `requestAnimationFrame` + easeOutCubic, respetando reduced-motion.

## Visual QA cuando el browser tool está bloqueado por permisos
Cuando Chrome pide "Allow remote debugging" (popup que un agente no puede aceptar), NO te quedes
bloqueado: usa **Chrome headless directo** para capturar y el **VLM local** para inspeccionar.
```bash
CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless --disable-gpu --window-size=1500,1000 \
  --screenshot="$LOCALAPPDATA/Temp/shot.png" --virtual-time-budget=9000 http://127.0.0.1:8124/index.html
```
Luego reduce la imagen (VLM local rechaza imágenes >~100KB de base64 con HTTP 400):
```python
from PIL import Image
im = Image.open(r'shot.png'); im.thumbnail((850,1100))
im.convert('RGB').save(r'shot.jpg', quality=72)   # ~50-70KB, aceptable
```
Y envíala a `qwen25vl-ablit:latest` (Ollama) para QA por secciones (ver skill `local-ollama-vision`).
Esto dio QA real en este proyecto cuando el browser estaba bloqueado.

## Auditoría de código antes de entregar (el usuario EXIGE esto)
El usuario pidió "audita todo, aunque te tardes, quiero pulido y fluido". Patrón que funcionó:
1. **Node linter inline** (sin deps): extraer `<script>` y `new Function(code)` para validar sintaxis;
   contar llaves CSS `{`/`}` balanceadas; chequear que cada `getElementById(id)` existe en el HTML;
   que cada `querySelector('.cls')` tiene la clase en CSS.
2. **Chequeo de funciones**: colectar `function X`, `const X=`, `let X=` y verificar que toda llamada
   tiene definición.
3. **Falsos negativos del auditor**: `undefined` legítimo de ECharts (`areaStyle:...:undefined`) y
   `min-width` no son bugs — el auditor debe excluir esas líneas o dará ruido.
4. **Python**: `python -m py_compile *.py` + probar **casos límite** (df vacío, serie constante,
   NaN) — ver skill `orderflow-volume-profile` para los bugs exactos que esto atrapó.
5. **Accesibilidad**: `aria-label` en botones, `aria-hidden` en iconos decorativos, `role="button"`
   + `tabindex="0"` + Enter/Espacio en nav, `aria-live` en secciones que cambian, teclado.
6. **End-to-end**: `curl /api/run` debe devolver `{"ok":true}` y el JSON actualizarse.

## Bugs de runtime JS que el linter estático NO detecta (depuración con consola headless)
Los linters (`new Function(code)`, balance de llaves) validan SINTAXIS, no RUNTIME. Los bugs de
runtime dan **pantalla en blanco** y solo se ven en consola. PATRÓN verificado 2026-09-01:
```bash
"$CHROME" --headless --disable-gpu --window-size=1500,1000 \
  --enable-logging=stderr --screenshot=shot.png --virtual-time-budget=12000 http://127.0.0.1:8124/index.html \
  2>&1 | grep -iE "CONSOLE.*(error|uncaught|typeerror|referenceerror)"
# salida ej.: CONSOLE:698 "Uncaught (in promise) TypeError: s.val.startsWith is not a function"
```
Un screenshot que pesa ~150KB cuando antes ~300KB = pantalla en blanco. Un log de consola vacío
con screenshot grande = OK.

### Bug real #1: `.startsWith()` sobre número → TypeError → pantalla en blanco
Cuando los datos cambian de string a número (ej. el backtest real devuelve `net_usd` como
`438.38` NUMÉRICO, no string `"438.38"`), código que hacía `s.val.startsWith('+')` crashea.
Fix: `const valStr = String(s.val);` ANTES de cualquier `.startsWith`/`.endsWith`, y usar
`valStr` para el resto. También `Number(s.val)` en vez de `s.val>0` para valores numéricos.
Regla: cuando un campo puede venir como string O número del JSON, normalizar con `String()`
antes de operaciones de string.

### Bug real #2: selector que "no cambia" = estado recomputado a default cada render
Síntoma: el selector de activo (hero) muestra los botones pero al hacer click no cambia nada.
Causa: la función de render recalculaba el activo con `prim = F['BTC-USD'] ? 'BTC-USD' : ...`
en CADA llamada → siempre volvía a BTC, ignorando la selección. Fix: variable **global de
estado** que persiste la selección entre renders:
```js
let heroCurrent = 'BTC-USD';                      // estado persistente (fuera de la función)
function renderX(){ const prim = F[heroCurrent] ? heroCurrent : fallback; ... }
// handler del click: setear ESTADO, luego re-render de TODAS las secciones dependientes
btn.addEventListener('click', ()=>{ heroCurrent = b.dataset.herosym; renderHero(); renderAI(); renderMarket(); loadTradingViewChart(); });
```
Regla: si N secciones muestran el MISMO dato (hero, IA, lectura de mercado, gráfico), un cambio
de selección debe re-renderizarlas TODAS juntas vía un estado global compartido — nunca
recomputar el default dentro de cada función.

## "El sistema genera los números, no valores demo" (backtest endpoint)
El usuario pidió que las stats (Net R, Profit Factor, Win Rate...) vinieran del sistema, no de
valores hardcodeados de ejemplo. Patrón: `backtest.py` ejecuta la estrategia sobre OHLCV real
y escribe `backtest_output.json`; `run_server.py` expone `/api/backtest`; el frontend hace
`fetch('backtest_output.json')` al boot y usa esos números (con fallback a demo si no hay).
- `renderStats()` lee `btPrimary()` (primer activo sin error) y muestra sus métricas reales.
- `initCharts()` usa `bt.equity_curve` real si existe, si no `genEquity()` de demo.
- Botón "Backtest" en la topbar → `fetch('/api/backtest')` → recarga stats + gráficos.
- Regla: separar la fuente real de la demo con un guard (`if(bt && bt.net_r!==undefined)`),
  y que la demo sea SOLO fallback. Un activo perdedor en el backtest es información valiosa
  (te dice qué NO operar), no un error.

## Estado guardado (máquina de Gio)
- `C:\Users\<USER>\trading\quantdesk\` (index.html, run_server.py, JSONs copiados)
- `C:\Users\<USER>\trading\orchestration\` (pipeline_forecast_flow.py, integrate_pipeline_alerts.py, orderflow_profile.py)
- Puerto 8124 · endpoint health `/api/health` · endpoint run `/api/run` (~60s)

## UX / diseño — lecciones del usuario (correcciones explícitas, respetar SIEMPRE)
Estas correcciones salieron de feedback directo del usuario en 2026-09-01 al revisar QuantDesk.
Son preferencias de workflow de primera clase para construir/adaptar dashboards de trading:

1. **NO reinventar el layout: tomar patrones de plataformas externas probadas.** El usuario
   dijo literalmente: *"No es necesario que reinventes todo, toma ejemplos de herramientas ya
   construidas en plataformas externas... entiende que es una plataforma que se debe adaptar a mí"*.
   Cuando hay una imagen de referencia o un patrón conocido (ej. dashboard de backtesting tipo
   "Herman Trading": sidebar + headline numbers + equity + drawdown + heatmap + sesiones),
   replicarlo y ADAPTARLO a sus datos — no inventar secciones nuevas desde cero.

2. **Jerarquía de información = qué mercado ves PRIMERO.** El usuario corrigió: *"No está bien
   priorizada la gráfica ni la interpretación de qué mercado estamos viendo"*. Orden correcto:
   (1) **Hero del mercado** — qué activo estás viendo (símbolo + nombre + precio grande +
   dirección + régimen + selector de activo), (2) **Interpretación** (IA + lectura del mercado),
   (3) **Gráfico en vivo**, (4) **métricas de rendimiento** de su operativa al final. NO empieces
   por las métricas.

3. **Globos de ayuda (tooltips) en CADA sección y botón.** El usuario pidió explícitamente
   *"globos de ayuda de interpretación de cada cosa, botón o interfaz"*. Los `title=` nativos
   del navegador NO bastan (feos, difíciles de alcanzar). Implementar un sistema de tooltips
   propios: icono `i` junto a cada sección/botón que al hover/focus muestra una burbuja con
   título + explicación. Ver el bloque CSS `.help` + `.help-bubble` en index.html como plantilla.

4. **La plataforma se adapta al usuario, no al revés.** El foco es "datos cargados para mi
   ventaja a la hora de determinar un resultado, bajo mi previo análisis". Cada sección debe
   alimentar una decisión concreta de trading (niveles → dónde entrar/salir; régimen → cómo
   operar; riesgo → cuánto arriesgar), no ser decorativa.

5. **Adaptar el universo de activos ANTES de construir** (ver sección "MERCADO DE GIO" en SKILL.md).
   No asumas SPY/QQQ/VIX; Gio opera forex/cripto/oro/Polymarket.

