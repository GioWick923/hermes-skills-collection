---
name: openmythos-rdt
description: "Looped transformers/RDT (OpenMythos): MLA, MoE, ACT."
version: 1.0.0
author: Hermes Agent (adoptado del repo kyegomez/OpenMythos, MIT)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mlops, architecture, looped-transformers, mla, moe, act]
    related_skills: [local-gguf-deployment, local-llm-picker, hermes-self-evolution]
---

# OpenMythos / Recurrent-Depth Transformers (RDT) — conocimiento adoptado

## When to Use

- Alguien menciona OpenMythos, Claude Mythos, looped/recurrent-depth transformers (RDT),
  MLAttention (MLA), ACT halting, depth extrapolation, o "looped MoE".
- Evaluar si un repo de arquitectura "teórica" vale la pena (veredicto honesto incluido).
- Elegir modelos locales y entender por qué DeepSeek/Qwen usan MLA o MoE.
- Responder "¿podemos usar X para razonar más sin más parámetros?" (test-time compute scaling).

## Qué es (veredicto honesto)

OpenMythos (kyegomez/OpenMythos, MIT, ~15k stars, 2026-04) es la **reconstrucción teórica**
de la arquitectura de "Claude Mythos" (modelo secreto de Anthropic, nunca publicado).
**NO es un modelo usable**: 0 releases, sin pesos entrenados, último commit 2026-05-23
(muerto). Es una hipótesis de arquitectura en PyTorch limpio + un inventario de
investigación pública (Parcae, COCONUT, DeepSeek, Saunshi, Graves).

Valor real: **educativo y conceptual** — es una de las mejores referencias públicas de
looped transformers implementados. Clone local: `C:/Users/<USER>/OpenMythos`.

## Arquitectura (la hipótesis)

```
Tokens → [Prelude: L capas transformer densas] → [RecurrentBlock: 1 bloque looped T veces]
        → [Coda: L capas transformer densas] → logits
```

- **Prelude/Coda**: bloques transformer estándar (densos, sin MoE), run una vez.
- **RecurrentBlock**: UN solo TransformerBlock (con MoE) reutilizado T veces por forward pass.
  Mismos pesos, más loops = más razonamiento profundo, sin crecer parámetros.
- **Razonamiento en espacio latente continuo**: no hay tokens intermedios (≠ chain-of-thought).
- Update por loop: `h_{t+1} = A·h_t + B·e + Transformer(h_t, e)` donde `e` = salida del
  Prelude congelada (inyección anti-drift en cada paso).

## 5 mecanismos clave (lo absorbible)

1. **LTIInjection (Parcae, Prairie et al. 2026)** — estabilidad garantizada por construcción:
   `A_discrete = exp(-exp(log_dt + log_A))` → diagonal con valores ∈ (0,1) → **ρ(A) < 1 siempre**.
   Resuelve la inestabilidad de entrenamiento de los looped transformers. Truco: ZOH
   discretización en log-space para evitar NaN (0·∞).
2. **ACTHalting (Graves, 2016)** — compute variable por posición: cada token acumula
   probabilidad de "parar" por loop; tokens fáciles salen temprano, difíciles reciben más
   cómputo, todo en el mismo batch. Remanente: weight = min(1-cum_p, p) en el paso final.
3. **MoE FFN (DeepSeekMoE, Dai et al. 2024)** — expertos finos top-K ruteados + shared experts
   siempre activos (absorben patrones comunes). El router elige DISTINTO subconjunto por loop
   → loop 3 ≠ loop 10 (misma computación ≠ misma función).
4. **MLA (DeepSeek-V2, 2024)** — atención multi-latente: cachea `c_kv` comprimido (low-rank)
   + k_rope en vez de K/V completos → **10-20x menos memoria KV cache** a producción.
   Q también se comprime: q_down → q_norm → q_up_nope + q_up_rope.
5. **loop_index_embedding + LoRAAdapter** — señal sinusoidal del índice de loop (≈ posicional
   del loop à la RoPE) + adaptador LoRA por profundidad para diferenciar iteraciones.

## Research grounding (papers reales, 2024-2026)

| Paper | Aporte |
|---|---|
| Parcae / Prairie et al. 2026 (UCSD+Together) | Estabilidad LTI; 770M RDT ≈ 1.3B dense |
| COCONUT (Meta FAIR, 2024) | Razonamiento en espacio latente continuo |
| Saunshi et al. 2025 | Looped transformers: depth extrapolation (train N loops → test N+k) |
| DeepSeek-V2 (2024) | MLA (KV cache comprimido) |
| DeepSeekMoE (2024) | Fine-grained MoE + shared experts |

## Takeaways para nuestro stack

- **Depth extrapolation** = el knob de razonamiento es de INFERENCIA, no de parámetros:
  más loops = más "pensar". Concepto detrás del test-time compute scaling.
- **MLA** explica por qué DeepSeek corre contextos largos con menos memoria — relevante al
  elegir modelos para 3060 12GB.
- **ACT** = compute adaptativo: la idea de "easy tokens early exit" ya está en modelos
  modernos (thinking budget de Qwen, etc.).
- Un RDT 770M-3B entrenado igualaría un dense 1.3B-5B (si Parcae escala) → candidato ideal
  para hardware modesto... CUANDO alguien entrene pesos. Hoy nadie lo ha hecho.

## Pitfalls verificados (2026-08-27)

- 🔴 **Sin pesos**: no hay checkpoint en ningún lado (0 releases, repo de 28 archivos).
  `pip install open-mythos` solo te da arquitectura random-init.
- 🔴 **Entrenar cuesta fortuna**: script 3B en FineWeb-Edu ≈ $100-500K en H100s. Una RTX 3060
  no alcanza ni de lejos.
- 🟡 **Bug en el README del repo**: su ejemplo `torch.linalg.eigvals(A)` truena porque
  `get_A()` devuelve vector 1-D diagonal → usar `A.abs().max()` (los eigenvalores de una
  diagonal son sus elementos).
- 🟡 **Bug en test suite del repo**: 12/75 tests fallan por la MISMA causa — pasan `freqs`
  completas (len=max_seq_len=32) a GQAttention/MLAttention/TransformerBlock/RecurrentBlock
  cuando T=8. `apply_rope` exige freqs cortadas a las posiciones exactas (docstring lo dice).
  El modelo real SÍ corta (`freqs_cis[start_pos:start_pos+T]` en `OpenMythos.forward`).
  Los 63 tests restantes pasan, incluido el model-level completo.
- 🟡 **Repo dormido**: último commit 3 meses antes de esta verificación. No esperar fixes.

## Smoke test reproducible (verificado ✅ CPU, torch 2.13)

```python
import torch, sys; sys.path.insert(0, "C:/Users/<USER>/OpenMythos")
from open_mythos.main import OpenMythos, MythosConfig
base = dict(vocab_size=1000, dim=256, n_heads=8, max_seq_len=128, max_loop_iters=4,
            prelude_layers=1, coda_layers=1, n_experts=8, n_shared_experts=1,
            n_experts_per_tok=2, expert_dim=64, lora_rank=8)
cfg = MythosConfig(**base, n_kv_heads=2)                    # GQA
# o MLA: MythosConfig(**base, n_kv_heads=8, kv_lora_rank=32, q_lora_rank=64,
#                     qk_rope_head_dim=16, qk_nope_head_dim=16, v_head_dim=16)
model = OpenMythos(cfg)
ids = torch.randint(0, 1000, (2, 16))
logits = model(ids, n_loops=4)                              # (2, 16, 1000)
out = model.generate(ids, max_new_tokens=8, n_loops=4)      # (2, 24)
rho = model.recurrent.injection.get_A().abs().max().item()  # 0.3679 = 1/e, < 1 ✅
```

Resultados observados: GQA=13.9M params vs MLA=1.5M a esa escala (MLA ~9x más compacto);
ρ(A) inicial = 1/e ≈ 0.368 (estable por diseño). Forward+generate corren en CPU <1s.

## Regla de oro

Si alguien pregunta "¿podemos usar OpenMythos?": la respuesta honesta es — como modelo, NO
(sin pesos); como referencia de arquitectura y conceptos (looped transformers, MLA, MoE,
ACT, estabilidad LTI), SÍ, y este skill es la puerta de entrada. No intentar entrenarlo
en hardware local.
