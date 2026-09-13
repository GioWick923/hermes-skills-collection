---
name: hermes-voice-hook
description: Hook voz Dalia optimizado para Hermes.
---

# Voice Hook Optimizado

Respuestas más rápidas, largas y coherentes con voz Dalia.

## Mejoras aplicadas

- **Velocidad**: RATE +15% (más dinámico)
- **Longitud**: _smart_extract() extrae máximo significado
- **Coherencia**: Mantiene contexto completo, no corta frases
- **Pre-cache**: Frases comunes ya definidas

## Uso

```python
from hermes_voice_hook import speak_response

# Respuesta larga y coherente
speak_response("Sí, Gio. Entiendo lo que necesitas y voy a...")

# Respuesta corta automática
speak_response("ok")  # Dice "Ok, ya voy"
speak_response("listo")  # Dice "Listo"
```

## Configuración

- Voz: es-MX-DaliaNeural (+27Hz, +15%)
- ffplay: C:\Users\<USER>\AppData\Local\hermes\tools\ffmpeg\bin\ffplay.exe
