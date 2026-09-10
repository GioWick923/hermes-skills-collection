---
name: shrimply
description: "Shrimply video editor integration — TTS, lip-sync, captions, rendering. Use when user needs video editing, speech synthesis for video, or automated caption generation."
metadata:
  hermes:
    tags: [video, editor, tts, shrimply, lip-sync]
    category: media
---

# Shrimply — Video Editor for Hermes

Editor de video en Rust con integración de TTS, lip-sync y generación de captions.

## Estado actual

**Repo clonado:** `C:\Users\<USER>\shrimply`

**Build:** Requiere Linux/WSL (GTK4 + CUDA + Slang)
- Windows nativo: No disponible (pre-alpha)
- Docker/Flatpak: Alternativa viable

## Uso con Hermes

### Vía MCP (recomendado)
```bash
# Iniciar server MCP de Shrimply
cd ~/shrimply && make mcp
```

### Comandos clave

```bash
# Build (Linux/WSL)
make build-gtk

# Run editor
make run-gtk

# Build server TTS
cd server && python -m shrimply_tts

# Export video
make export PROJECT=file.shrimp
```

## Integración con OmniVoice

Shrimply tiene soporte nativo para TTS:
- Voice cloning desde referencia
- Voice design con atributos
- Lip-sync automático

## Características principales

| Feature | Estado |
|---------|--------|
| Edición de video | ✅ GTK editor |
| TTS integrado | ✅ IndexTTS Beta |
| Lip-sync | ✅ Rhubarb (Rust port) |
| Captions | ✅ MCP bulk insertion |
| Manim bridge | ✅ Para animaciones |
| Blender bridge | ✅ Para 3D |

## Dependencias requeridas

```bash
# Linux (Ubuntu/Fedora)
sudo apt install libgtk-4-dev libadwaita-1-dev \
    ffmpeg libavcodec-dev libavformat-dev \
    cuda-toolkit slang-optixlang

# WSL2
# Misma que Linux + CUDA driver
```

## Scripts útiles

```python
# server/tts_client.py — Cliente para TTS server
# crates/media/audio/tts/ — Módulo TTS en Rust
```

## Links

- [Docs](https://shrimply.pages.dev)
- [Issues](https://github.com/soirihiroka/shrimply/issues)
- [Discord/Comunidad](https://github.com/soirihiroka/shrimply#discussion--communication)

## Notas

- Pre-alpha: Expect bugs y cambios de API
- CUDA required para aceleración GPU
- Lip-sync model requiere download (~50MB)
