---
name: omnivoice
description: "State-of-the-art TTS model with 600+ languages, voice cloning, and voice design. Use when user wants text-to-speech, voice cloning, audio generation, or multilingual TTS."
metadata:
  hermes:
    tags: [tts, audio, voice, omnivoice, speech]
    category: media
---

# OmniVoice — Text-to-Speech for Hermes

OmniVoice es un modelo TTS (text-to-speech) state-of-the-art que soporta:
- **600+ idiomas**
- **Voice cloning** (clonar voz desde audio de referencia)
- **Voice design** (crear voces con atributos: gender, age, pitch, accent)
- **Velocidad**: 40x más rápido que tiempo real

## Requisitos

- GPU NVIDIA con CUDA (RTX 3060+ recomendado)
- PyTorch 2.8.0+ con soporte CUDA
- OmniVoice instalado: `pip install omnivoice`

## Uso básico

```python
from omnivoice import OmniVoice
import soundfile as sf
import torch

# Cargar modelo
model = OmniVoice.from_pretrained(
    "k2-fsa/OmniVoice",
    device_map="cuda:0",
    dtype=torch.float16
)

# 1. Voz automática
audio = model.generate(text="Hola mundo")
sf.write("output.wav", audio[0], 24000)

# 2. Voice cloning (desde referencia)
audio = model.generate(
    text="Tu texto aquí",
    ref_audio="referencia.wav",
    ref_text="Transcripción de referencia"
)

# 3. Voice design (atributos)
audio = model.generate(
    text="Hello world",
    instruct="male, low pitch, british accent"
)
```

## Comandos CLI

```bash
# Demo web local
omnivoice-demo --ip 0.0.0.0 --port 8001

# Inferencia por lotes
omnivoice-infer-batch \
    --model k2-fsa/OmniVoice \
    --test_list test.jsonl \
    --res_dir results/ \
    --batch_size 8
```

## Integración con Hermes

### Skill: `/tts <text>`
Genera audio desde texto usando OmniVoice.

### Skill: `/voice-clone <audio> <text>`
Clona voz desde audio de referencia.

### Skill: `/voice-design <text> <attributes>`
Crea voz con atributos específicos.

## Parámetros avanzados

```python
audio = model.generate(
    text="...",
    num_step=32,      # pasos de difusión (16 para más rápido)
    speed=1.0,        # factor de velocidad (>1 más rápido)
    duration=10.0,    # duración fija en segundos
    normalize_text=True,  # normalizar números a palabras
)
```

## Control de pronunciación

```python
# Símbolos no-verbales
audio = model.generate(text="Hello [laugh] world")

# Corrección de pronunciación (pinyin/fonemas)
audio = model.generate(text="Hello [B EY1 S] world")
```

## Links

- [GitHub](https://github.com/k2-fsa/OmniVoice)
- [HuggingFace](https://huggingface.co/k2-fsa/OmniVoice)
- [Demo online](https://huggingface.co/spaces/k2-fsa/OmniVoice)
- [Papel](https://arxiv.org/abs/2604.00688)

## Notas

- El modelo requiere ~10GB VRAM en FP16
- Voice cloning funciona mejor con referencias de 3-10 segundos
- El rendimiento es ~40x realtime en RTX 3060
