---
category: mlops
name: local-gguf-deployment
description: "Use when choosing GGUF quantizations for local VRAM."
version: 1.0.0
author: Gio
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [gguf, quantization, vram, ollama, llama.cpp, local-model, evaluation]
    related_skills: [local-llm-picker, llama-cpp, ollama, local-ablit-delegation]
---

# Evaluación e instalación de GGUFs locales

Clase de trabajo: evaluar si un modelo GGUF cabe en VRAM, descargarlo, instalarlo en Ollama
(o llama.cpp server), y verificar velocidad real.

## When to Use
- User wants to know if a model can run on their local GPU.
- User asks to download + install a new GGUF from HuggingFace.
- Need to pick the best quantization for available VRAM.
- Ollama or llama.cpp setup for a new model.

## Workflow

### 1. Evaluar hardware
```bash
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader  # VRAM
cat /proc/meminfo | head -3  # RAM total (Linux/WSL)
free -h  # alternativa
```
Regla: para que corra "bien" (sin offload masivo a CPU), la cuantización debe caber
~90-100% en VRAM. Si VRAM=12GB y RAM=96GB, el offload CPU es tolerable (5-15 tok/s en 27B)
pero para velocidad real (>15 tok/s) la cuantización debe caber por completo.

### 2. Verificar tamaños GGUF en HF + Estrategia MoE

Los modelos MoE (Mixture of Experts) tienen **parámetros totales vs activos**:
- Ej: `GLM-4.7-Flash` = 30B totales, solo **~3B activos** por token
- Ej: `Gemma4-26B-A4B` = 26B totales, solo **4B activos** por token
- **Regla MoE**: si los activos caben en VRAM, el modelo corre fluido aunque tenga
  10x params totales. El offload solo mueve expertos inactivos a RAM.

```bash
# HEAD request da tamaño real (más confiable que tree API)
curl -sI "https://huggingface.co/{AUTHOR}/{REPO}/resolve/main/{ARCHIVO}.gguf" | \
  grep -i content-length | awk '{print $2/(1024^3)" GB"}'
```

**Guía de cuantizaciones para RTX 3060 12GB (Windows, CUDA 13.3):**

| Cuantización | Tamaño típico | VRAM 3060 12GB | Velocidad est. | Cuándo usarla |
|-------------|---------------|----------------|----------------|---------------|
| IQ1_S/IQ1_M | ~10-13 GB | ✅ 100% | 25-35 tok/s | Solo si desesperas |
| **IQ2_M** | **9-11 GB** | ✅ **100%** | **25-35 tok/s** | **Cabe completo, calidad baja** |
| **IQ3_M** | **12-15 GB** | ⚡ **~90-95%** | **15-25 tok/s** | ⭐ **Mejor balance calidad/VRAM** |
| Q3_K_M/Q3_K_L | 13-15 GB | ⚡ ~85% | 12-20 tok/s | Alternativa IQ3 |
| Q4_K_S | 14-16 GB | ⚡ ~75% | 8-15 tok/s | Mejor calidad, más offload |
| Q4_K_M | 16-18 GB | ⚡ ~65% | 6-12 tok/s | Calidad óptima, lento |
| Q5_K_M | 19-22 GB | 🔴 ~50% | 4-8 tok/s | Muy lento |
| Q6_K | 22-25 GB | 🔴 ~40% | 2-5 tok/s | Solo con VRAM>16GB |
| Q8_0 | 30-35 GB | 🔴 offload masivo | <2 tok/s | Solo GPU>24GB |

**Con 96 GB RAM + 12 GB VRAM**: IQ3_M es el sweet spot. Solo ~0.7-1.5 GB offload a RAM,
velocidad casi completa. Usar `ngl 99` (llama-server) o `num_gpu 999` (Ollama) para offload máximo.

**Para MoE específicamente**: Priorizar cuantizaciones IQ sobre Q en MoE (IQ maneja mejor
la distribución de expertos). Usar `fused_moe=1` en llama-server para aceleración MoE.

### 2b. Inferencia heterogénea (ktransformers) — el cuello de botella es RAM, no VRAM
Para correr MoE gigantes (DeepSeek-R1 671B, Qwen3-Next 235B) con poca VRAM, ktransformers
mueve expertos "fríos" a RAM. La pregunta determinante es **¿cabe el modelo Q4 en tu RAM total?**
(~0.55-0.6 GB/1B params totales). Con 96GB RAM: DS-R1 pide 382GB (NO), Qwen3-Next ~120GB (NO),
solo Qwen2-57B-A14B (34GB) y Mixtral-8x22B (86GB) caben. Build en Windows es manual (cmake+MSVC,
solo install.sh en Linux). Detalle completo: `references/ktransformers-heterogeneous-inference.md`.

### 3. Verificar arquitectura (compatibilidad con Ollama/llama.cpp)
Revisar los tags del repo HF:
- `gated-deltanet`, `hybrid-attention` → arquitectura **nueva**; Ollama 0.32.14 puede NO cargarla.
  Usar llama.cpp server (binarios CUDA recientes) con `--spec-type draft-mtp` si el modelo
  tiene MTP.
- `mtp` → usa llama.cpp con `--spec-type draft-mtp --spec-draft-n-max 3` para aceleración
  (predice N tokens por paso).
- Error típico de Ollama: `command must be one of "from", "license", "template", ...`
  (PROJECTOR no soportado desde 0.32.14 para mmproj).

### 4. Descarga acelerada con hf-transfer

```bash
# Instalar acelerador Rust (descarga paralela)
pip install hf-transfer -U -i https://pypi.org/simple

# Usar con huggingface-cli:
HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download \
  AUTHOR/MODEL \
  --include "*.gguf" \
  --local-dir "$LOCALAPPDATA/hermes/models/NOMBRE"
```

**Alternativa rápida con curl** (cuando solo necesitas 1 archivo):
```bash
mkdir -p "$LOCALAPPDATA/hermes/models/NOMBRE"
curl -L -o "archivo.gguf" "URL_DE_DESCARGA" --progress-bar
```

**Verificar tamaño real ANTES de descargar** (HF API a veces reporta 0 bytes):
```bash
curl -sI "https://huggingface.co/{AUTHOR}/{REPO}/resolve/main/{ARCHIVO}.gguf" | \
  grep -i content-length | awk '{print $2/(1024^3)" GB"}'
```

- **Siempre en background** con `notify_on_complete=true` (modelos de 10-15GB tardan 15-40 min).
- Monitorear progreso con `process(action='poll')`.
- Verificar integridad: si el repo publica SHA256, descargarlo y verificar al terminar.

### 5. Instalación en Ollama
```bash
# Modelfile mínimo
FROM C:/Users/.../ruta/al/modelo.gguf
PARAMETER temperature 0
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 8192
PARAMETER num_predict 2048

# Crear
cd "$LOCALAPPDATA/hermes/models/{NOMBRE}" && ollama create {nombre} -f Modelfile
```
- **NO usar PROJECTOR** en Ollama 0.32.14 (comando no válido). Para multimodal, crear sin
  mmproj primero y resolver visión aparte.
- `ollama create` copia el GGUF a la caché de Ollama (~13GB → ~3-5 min de copia). Usar
  `background=true` porque el timeout del terminal puede dispararse.
- Verificar: `ollama list | grep {nombre}`.

### 6. Instalación en llama.cpp server (alternativa)
Si Ollama no carga la arquitectura, usar los binarios CUDA:
```bash
# binarios en $LOCALAPPDATA/hermes/llama-cpp/ (ya compilados con CUDA 13.3)
cd "$LOCALAPPDATA/hermes/llama-cpp"
./llama-server -m /ruta/al/modelo.gguf --host 127.0.0.1 --port 8080 \
  -c 8192 --split-mode layer
# Para modelos con MTP:
./llama-server -m modelo.gguf --spec-type draft-mtp --spec-draft-n-max 3 \
  --host 127.0.0.1 --port 8080 -c 8192
```
- Sirve endpoint OpenAI-compatible en `http://127.0.0.1:8080/v1`.
- Apuntar clientes/ablit a ese endpoint.

### 7. Medir velocidad real
```bash
ollama run {modelo} "Responde solo OK" --verbose 2>&1 | grep -E "eval rate|total duration"
```
- `eval rate` = tokens/s reales (la métrica que importa para el usuario).
- `prompt eval rate` = primera carga (lenta si el modelo no está en caché).
- Si el modelo es nuevo, la primera carga incluye ~30-40s de load.

### 8. Limpieza de modelo viejo (cuando se reemplaza)
```bash
# Remover de Ollama
ollama rm {nombre-viejo}

# Remover GGUF
rm "$LOCALAPPDATA/hermes/models/{/ruta/al/archivo}.gguf"
rm -rf "$LOCALAPPDATA/hermes/models/{carpeta-vieja}"
```
- Confirmar con el usuario antes (operación destructiva, ~13GB).
- Actualizar `ablit` y la skill correspondiente con el nuevo modelo.

## Pitfalls
- **Timeout de terminal en `ollama create`**: el comando copia 13GB y el parser de GGUF
  puede exceder el timeout por defecto (180s). Usar `background=true, notify_on_complete=true`
  con timeout de 3600s.
- **Timeout de terminal en `ablit ask`**: el modelo lento (~6 tok/s) con thinking largo
  puede exceder 300s. Fix: usar `--num 150` + pedir respuesta corta en el prompt.
- **nvidia-smi no muestra VRAM libre en git-bash**: funciona igual; usar `nvidia-smi --query-gpu=...`
  en cmd o PowerShell.
- **PROJECTOR no soportado**: Ollama 0.32.14 no acepta `PROJECTOR` en Modelfile. Si el modelo
  necesita mmproj, crear primero sin PROJECTOR (texto puro) y resolver visión aparte.
- **Verificar VRAM libre ANTES de lanzar modelo**: si hay otras apps pesadas abiertas,
  la VRAM disponible puede ser menor que el total de la tarjeta.