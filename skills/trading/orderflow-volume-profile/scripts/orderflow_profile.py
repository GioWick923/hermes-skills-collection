"""Order-Flow Profile en Python: POC, Area de Valor (VAH/VAL), Delta, Imbalance, OVL, Balance tilt.
Portado de la logica del indicador Pine 'Volume Footprint' (ata_sabanci VFP-Intro) con datos
reales de mercado (yfinance), no estimacion geometrica.

Incluye las guardas de robustez (auditoria 2026-09-01): serie constante, df vacio,
1 fila, NaN -> nunca truena.
"""
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf


# ---------------------------------------------------------------------------
# Datos de mercado
# ---------------------------------------------------------------------------
def get_ohlcv(ticker: str, period: str = "3mo", interval: str = "1h") -> pd.DataFrame:
    """Descarga OHLCV real de yfinance."""
    df = yf.download(ticker, period=period, interval=interval,
                     progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    return df


# ---------------------------------------------------------------------------
# Perfil de volumen (distribucion por niveles de precio)
# ---------------------------------------------------------------------------
@dataclass
class VolumeProfile:
    """Perfil de volumen: distribuye el volumen de cada barra en filas de precio."""
    price_rows: np.ndarray          # niveles de precio (de menor a mayor)
    buy_vol: np.ndarray             # volumen compra por fila
    sell_vol: np.ndarray            # volumen venta por fila
    total_vol: np.ndarray           # volumen total por fila
    imb_pct: float = 300.0          # umbral de imbalance diagonal (300% = clasico)

    @property
    def poc(self) -> float:
        """Precio de control: el nivel con mayor volumen."""
        return float(self.price_rows[int(np.argmax(self.total_vol))])

    @property
    def value_area(self) -> tuple[float, float]:
        """Limites del area de valor (70% del volumen): (VAH, VAL)."""
        total = self.total_vol.sum()
        if total == 0:
            return float(self.poc), float(self.poc)
        target = total * 0.70
        poc_idx = int(np.argmax(self.total_vol))
        cum = 0.0
        lo, hi = poc_idx, poc_idx
        while cum < target and (lo > 0 or hi < len(self.total_vol) - 1):
            up = self.total_vol[hi + 1] if hi < len(self.total_vol) - 1 else -1
            down = self.total_vol[lo - 1] if lo > 0 else -1
            if up >= down:
                hi += 1
                cum += up
            else:
                lo -= 1
                cum += down
        vah = float(self.price_rows[hi])
        val = float(self.price_rows[lo])
        return (vah, val)

    @property
    def delta(self) -> float:
        """Delta neto total (compra - venta) en el perfil."""
        return float((self.buy_vol - self.sell_vol).sum())

    @property
    def imbalance(self) -> float:
        """Desequilibrio relativo: (buy - sell) / (buy + sell). [-1, 1]."""
        b, s = self.buy_vol.sum(), self.sell_vol.sum()
        if b + s == 0:
            return 0.0
        return float((b - s) / (b + s))

    # -- Metricas portadas del Pine VFP-Intro --
    def diagonal_imbalance(self) -> list[dict]:
        """Imbalance DIAGONAL (definicion clasica del Pine, 300% por defecto).

        Nivel k tiene imbalance de compra si buy[k] > sell[k-1]*ratio (sella el lado de abajo).
        De venta si sell[k] > buy[k+1]*ratio. La diagonal cruza niveles vecinos porque el
        desequilibrio se lee en la frontera entre dos precios.
        """
        n = len(self.buy_vol)
        ratio = self.imb_pct / 100.0
        out = []
        for k in range(n):
            b, s = self.buy_vol[k], self.sell_vol[k]
            if k >= 1 and b > 0 and self.sell_vol[k - 1] > 0 and b > self.sell_vol[k - 1] * ratio:
                out.append({"price": float(self.price_rows[k]), "level": k,
                            "kind": "buy", "ratio": b / self.sell_vol[k - 1]})
            if k <= n - 2 and s > 0 and self.buy_vol[k + 1] > 0 and s > self.buy_vol[k + 1] * ratio:
                out.append({"price": float(self.price_rows[k]), "level": k,
                            "kind": "sell", "ratio": s / self.buy_vol[k + 1]})
        return out

    @property
    def imbalance_levels(self) -> list[dict]:
        """Primer nivel imbalanced arriba y abajo del POC (regla 'chart' del Pine)."""
        n = len(self.buy_vol)
        poc = int(np.argmax(self.total_vol))
        diag = self.diagonal_imbalance()
        if not diag:
            return []
        up = next((d for d in diag if d["level"] > poc), None)
        dn = next((d for d in reversed(diag) if d["level"] < poc), None)
        return [d for d in (dn, up) if d is not None]

    @property
    def ovl(self) -> float:
        """Overlapping coefficient: cuanto compra/venta comparten precios, 0-1.
        ~1 balanceado/rotativo; ~0 direccional (cada lado en su territorio)."""
        b, s = self.buy_vol.sum(), self.sell_vol.sum()
        if b <= 0 or s <= 0:
            return 0.0
        nb = self.buy_vol / b
        ns = self.sell_vol / s
        return float(np.minimum(nb, ns).sum())

    @property
    def balance_tilt(self) -> float:
        """% desequilibrio del volumen total. + = compra domina, - = venta."""
        b, s = self.buy_vol.sum(), self.sell_vol.sum()
        if b + s <= 0:
            return 0.0
        return float(100.0 * (b - s) / (b + s))


def build_profile(df: pd.DataFrame, rows: int = 25,
                  spread_factor: Optional[float] = None,
                  imb_pct: float = 300.0) -> VolumeProfile:
    """Construye el perfil de volumen a partir de OHLCV.

    Reparte el volumen de cada barra por sus filas de precio (uniforme por rango),
    buy/sell segun direccion de la vela (close>=open => buy). Con guardas de robustez:
    df vacio, NaN, rango cero (precios constantes) -> nunca truena.
    """
    hilo = df[["High", "Low", "Volume", "Open", "Close"]].to_numpy(dtype=float)
    hi, lo, vol, o, c = hilo[:, 0], hilo[:, 1], hilo[:, 2], hilo[:, 3], hilo[:, 4]

    # Guarda: datos vacios
    if len(hi) == 0 or np.isnan(lo).all() or np.isnan(hi).all():
        return VolumeProfile(np.array([0.0]), np.zeros(1), np.zeros(1), np.zeros(1), imb_pct)

    # Guarda: NaN / rangos no finitos -> limpiar
    finite = np.isfinite(hi) & np.isfinite(lo) & np.isfinite(c) & np.isfinite(o)
    if not finite.all():
        keep = finite & (vol > 0)
        if keep.any():
            hi, lo, vol, o, c = hi[keep], lo[keep], vol[keep], o[keep], c[keep]
        else:
            return VolumeProfile(np.array([0.0]), np.zeros(1), np.zeros(1), np.zeros(1), imb_pct)

    pmin, pmax = float(np.nanmin(lo)), float(np.nanmax(hi))
    # Guarda: rango cero (precios constantes) -> al menos 1 fila
    if pmax <= pmin:
        pmin, pmax = pmin - 1.0, pmax + 1.0
    if spread_factor is None:
        spread_factor = max((pmax - pmin) / rows, 1e-9)
    n = max(int(np.ceil((pmax - pmin) / spread_factor)), 1)
    price_rows = np.array([pmin + i * spread_factor for i in range(n)])

    buy_vol = np.zeros(n)
    sell_vol = np.zeros(n)
    total_vol = np.zeros(n)

    for i in range(len(hi)):
        idx_lo = int(max((lo[i] - pmin) / spread_factor, 0))
        idx_hi = int(min((hi[i] - pmin) / spread_factor, n - 1))
        if idx_hi < idx_lo:
            idx_lo, idx_hi = idx_hi, idx_lo
        span = idx_hi - idx_lo + 1
        if span <= 0:
            continue
        per_row = vol[i] / span
        is_buy = c[i] >= o[i]
        for j in range(idx_lo, idx_hi + 1):
            total_vol[j] += per_row
            if is_buy:
                buy_vol[j] += per_row
            else:
                sell_vol[j] += per_row

    return VolumeProfile(price_rows=price_rows, buy_vol=buy_vol,
                         sell_vol=sell_vol, total_vol=total_vol, imb_pct=imb_pct)


# ---------------------------------------------------------------------------
# Analisis consolidado
# ---------------------------------------------------------------------------
@dataclass
class ProfileAnalysis:
    poc: float
    vah: float
    val: float
    delta: float
    imbalance: float
    close: float
    location: str      # "arriba del VA", "dentro del VA", "abajo del VA", "sin datos"
    ovl: float = 0.0
    balance_tilt: float = 0.0
    balance_state: str = "neutral"
    imb_levels: list = field(default_factory=list)

    def summary(self) -> str:
        s = (f"POC={self.poc:.2f} | VAH={self.vah:.2f} | VAL={self.val:.2f} "
             f"| Delta={self.delta:+,.0f} | Imb={self.imbalance:+.2f} "
             f"| OVL={self.ovl:.2f} | Balance={self.balance_state}({self.balance_tilt:+.1f}%) "
             f"| close={self.close:.2f} | {self.location}")
        if self.imb_levels:
            lbls = [f"{d['kind']}@{d['price']:.2f}(x{d['ratio']:.1f})" for d in self.imb_levels]
            s += "\n  IMB diagonal: " + " | ".join(lbls)
        return s


def analyze(df: pd.DataFrame, rows: int = 25, imb_pct: float = 300.0,
            ovl_tilt: float = 5.0) -> ProfileAnalysis:
    """Analisis completo del perfil de volumen de un OHLCV."""
    prof = build_profile(df, rows=rows, imb_pct=imb_pct)
    vah, val = prof.value_area
    # Guarda: df vacio -> perfil neutral
    if df.empty or "Close" not in df.columns or len(df) == 0:
        return ProfileAnalysis(prof.poc, vah, val, prof.delta, prof.imbalance,
                               close=0.0, location="sin datos",
                               ovl=prof.ovl, balance_tilt=0.0, balance_state="neutral",
                               imb_levels=[])
    close = float(df["Close"].iloc[-1])
    if close > vah:
        loc = "arriba del VA"
    elif close < val:
        loc = "abajo del VA"
    else:
        loc = "dentro del VA"

    tilt = prof.balance_tilt
    if tilt >= ovl_tilt:
        bstate = "buy"
    elif tilt <= -ovl_tilt:
        bstate = "sell"
    else:
        bstate = "neutral"

    return ProfileAnalysis(prof.poc, vah, val, prof.delta, prof.imbalance,
                           close=close, location=loc, ovl=prof.ovl,
                           balance_tilt=tilt, balance_state=bstate,
                           imb_levels=prof.imbalance_levels)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    for tkr in ["SPY", "BTC-USD"]:
        print(f"\n=== {tkr} ===")
        try:
            df = get_ohlcv(tkr, period="3mo", interval="1h")
            a = analyze(df)
            print("OHLCV:", df.shape, "|", df.index[0].date(), "->", df.index[-1].date())
            print("RESUMEN:", a.summary())
        except Exception as e:
            print("ERROR:", e)

    # Test de robustez (no debe tronar):
    import numpy as np
    def mk(c, h, l, v, o):
        return pd.DataFrame({'Open': o, 'High': h, 'Low': l, 'Close': c, 'Volume': v})
    edge = {
        'constante': mk([100]*5, [100]*5, [100]*5, [500]*5, [100]*5),
        '1_fila': mk([100], [100], [100], [500], [100]),
        'vacio': pd.DataFrame(columns=['Open','High','Low','Close','Volume']),
        'NaN': mk([100, np.nan, 102], [102, np.nan, 104], [99, np.nan, 101], [1000, np.nan, 1300], [100, np.nan, 102]),
    }
    print("\n=== TEST ROBUSTEZ ===")
    ok = True
    for name, d in edge.items():
        try:
            analyze(d); print(f"  OK  {name}")
        except Exception as e:
            ok = False; print(f"  FAIL {name}: {type(e).__name__}: {e}")
    print("  " + ("TODOS LOS CASOS OK" if ok else "HAY FALLOS"))
