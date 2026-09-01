---
name: vram-watchdog
description: "Libera VRAM de modelos inactivos; recarga bajo demanda."
version: 1.0.0
author: Gio + Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [vram, watchdog, llama-cpp, modelo-local, auto-unload]
    related_skills: [local-gguf-deployment, local-ablit-delegation, local-model-install]
---

# VRAM Watchdog — libera VRAM de modelos inactivos

Sistema para PC con VRAM limitada (RTX 3060 12GB) que corre modelos locales (llama.cpp :8080):
cuando un modelo queda **inactivo 10 minutos**, se desmonta de VRAM automáticamente;
cuando se **requiere**, se recarga bajo demanda.

## Scripts

- `$LOCALAPPDATA/hermes/scripts/vram_watchdog.py` — vigilante (mata server inactivo)
- `$LOCALAPPDATA/hermes/scripts/model_manager.py` — carga/para/toca heartbeat

## Cómo funciona

1. **Heartbeat** (`$LOCALAPPDATA/hermes/models/.heartbeat`): se toca cuando hay actividad
   (conexiones al puerto 8080 detectadas por netstat, o `model_manager.py touch`).
2. **Watchdog** (corre por cron cada 2 min): si el server está vivo pero sin actividad
   durante 10 min → mata `llama-server.exe` (libera VRAM).
3. **Recarga**: cuando el agente necesita un modelo local, ejecuta:
   ```bash
   python "$LOCALAPPDATA/hermes/scripts/model_manager.py" start ablit   # qwen 27B MTP
   python "$LOCALAPPDATA/hermes/scripts/model_manager.py" start ornith  # Ornith 9B Q5
   ```

## Uso

```bash
# Watchdog (cron cada 2 min)
python "$LOCALAPPDATA/hermes/scripts/vram_watchdog.py"
python "$LOCALAPPDATA/hermes/scripts/vram_watchdog.py" --status
python "$LOCALAPPDATA/hermes/scripts/vram_watchdog.py" --force-kill  # probar

# Model manager
python "$LOCALAPPDATA/hermes/scripts/model_manager.py" start ornith
python "$LOCALAPPDATA/hermes/scripts/model_manager.py" start ablit
python "$LOCALAPPDATA/hermes/scripts/model_manager.py" stop
python "$LOCALAPPDATA/hermes/scripts/model_manager.py" touch
python "$LOCALAPPDATA/hermes/scripts/model_manager.py" status
```

## Modelos gestionados

| Nombre | Modelo | GGUF | Notas |
|--------|--------|------|-------|
| `ablit` | qwen3.8-27b-abliterated | `models/qwen38-27b-abliterated/qwen38-27b-abliterated-3.69bpw-12GB-MTP.gguf` | MTP, ~13 tok/s |
| `ornith` | Ornith-1.5-9B-uncensored | `models/Ornith-1.5-9B-uncensored/Ornith-1.5-9B-uncensored.Q5_K_M.gguf` | Q5_K_M 6.47GB, abliterado, multimodal |

## Cron

El watchdog se registró con:
- Schedule: `*/2 * * * *` (cada 2 min)
- Comando: `python $LOCALAPPDATA/hermes/scripts/vram_watchdog.py`

## Pitfalls

- **netstat en Windows devuelve codepage** (no UTF-8): usar `encoding="latin-1"` en subprocess,
  si no, `UnicodeDecodeError`.
- **El watchdog NO debe hacer HTTP al puerto** (falsos positivos de actividad): solo netstat.
- **TIME_WAIT cuenta como actividad reciente** (~2 min): suficiente para no matar un modelo
  que acaba de usarse.
- **`model_manager.py start` mata el server actual** si está arriba (asume que pides ese modelo).
- **Verificar VRAM libre antes de start**: si otro proceso pesado usa la GPU, el modelo
  puede no caber; usar `nvidia-smi`.
- **Primera carga de un modelo nuevo tarda**: 9B ~5-15s, 27B ~20-40s. El manager espera hasta 60s.

## Verificación

- [ ] `vram_watchdog.py --status` → detecta pids y actividad
- [ ] `vram_watchdog.py` con actividad → NO mata, toca heartbeat
- [ ] Inactivo 10 min → mata llama-server (VRAM libre)
- [ ] `model_manager.py start ornith` → server :8080 responde
- [ ] `model_manager.py touch` → heartbeat actualizado