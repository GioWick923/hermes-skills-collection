# ktransformers — inferencia heterogénea CPU+GPU (MoE gigantes)

Evaluado 2026-09-01 contra hardware real de Gio (RTX 3060 12GB + 96GB RAM + Xeon E5-2678 v3, AVX2-only).

## Qué es
`kvcache-ai/ktransformers`: framework de inferencia **heterogénea CPU+GPU** para modelos
MoE enormes. Mueve los expertos "calientes" a GPU y los "fríos" a RAM. Paper premiado SOSP'25.
Versión actual usa `kt-kernel` (build Linux-first) + fork `sglang-kt` para servir.

## REGLA CLAVE (el cuello de botella es RAM, no VRAM)
Para modelos grandes, los pesos expertos que no caben en GPU viven en **RAM**.
Por eso la pregunta determinante es **¿el modelo cabe en tu RAM total?**, NO en la VRAM.
Regla práctica: pesos Q4 ≈ 0.55–0.6 GB por 1B de parámetros **totales** (incluye todos los expertos).

### Tabla de referencia (Q4)
| Modelo | Params totales | RAM que pide | ¿Cabe en 96GB? |
|--------|---------------|-------------|----------------|
| DeepSeek-R1 / V3 (671B) | 671B | **382 GB** | ❌ NO |
| DeepSeek-V2 (236B) | 236B | 136 GB | ❌ NO |
| Qwen3-Next (235B-A22B) | 235B | ~120 GB | ❌ NO |
| Mixtral-8x22B | 141B | 86 GB | 🟡 al límite |
| **Qwen2-57B-A14B** | 57B | **34 GB** | ✅ SÍ |

**Conclusión para 96GB RAM:** los modelos estrella (DS-R1, Qwen3-Next) NO caben. Solo
Qwen2-57B-A14B y Mixtral-8x22B son viables. El upgrade que desbloquea DS-R1 = **RAM a 256GB+**,
no más VRAM. Antes de prometer utilidad de ktransformers, comparar peso del modelo Q4 vs RAM libre.

## Build en Windows (realidad)
- Build actual (kt-kernel): **Linux-first**, solo `install.sh`. En Windows se compila **manual**
  con cmake + MSVC (el `CMakeLists.txt` sí trae soporte WIN32/MSVC, pero no hay script).
- El `install.bat` nativo SOLO existe en `archive/` (versión vieja v0.2).
- Wheel PyPI (`pip install kt-kernel`) = **solo Linux** (manylinux). No hay wheel Windows.
- Requisitos para build Windows: VS BuildTools 2022 (C++), CUDA toolkit (nvcc), torch CUDA,
  y flash-attention (doloroso en Windows).

## Estado preparado en la máquina (dejado para futuro)
- Instalador **CUDA 12.6.1** completo → `$LOCALAPPDATA/Temp/cuda_12.6.1_560.94_windows.exe`
  (3074MB, verificado cabecera `MZ`). URL válida: `developer.download.nvidia.com/compute/cuda/12.6.1/local_installers/cuda_12.6.1_560.94_windows.exe`
- Venv `$LOCALAPPDATA/ktransformers/.venv-kt` con **torch 2.13.0+cu126** (RTX 3060 detectada ✅)
- Repo clonado → `$LOCALAPPDATA/ktransformers`
- Nota canónica → `Obsidian Vault/Memorias/Agente/KTransformers-Evaluacion.md`

## Decisión tomada
Build **detenido** (no vale la pena con 96GB RAM). Se dejó la descarga CUDA + venv para
cualquier futuro proyecto GPU. Revisitar solo si sube RAM a 256GB+ o hay necesidad real de Qwen2-57B.

## DLSS5oneclick (nota lateral, mismo estilo de evaluación "¿vale para mi hardware?")
`faisalkindi/DLSS5oneclick` v0.6.0: instalador 1-clic (exe Rust 14.8MB) del build filtrado de
DLSS 5 neural-rendering en cualquier juego DX11/DX12 con RTX 20-50 (RTX 3060 soportada).
- Dos rutas: con DLSS propio (ReShade+RenoDX) / sin DLSS (Feeder+LumeniteFX), o OptiScaler.
- Peros honestos: build filtrado/en desarrollo (calidad variable), modifica DLLs de juegos
  (Defender/SmartScreen puede marcarlo), DLSS5 NR es pesado (puede bajar FPS en 3060), y
  riesgo de ban en juegos online con anti-cheat (inyección de DLLs).
- Es pequeño, reversible (desinstala limpio). Vale para 1-2 juegos single-player con DLSS,
  para mejor nitidez, no para ganar FPS en 3060.
