---
category: nvidia-glm
name: nvidia-glm
version: "1.0.0"
description: "Chat streaming contra el modelo z-ai/glm-5.2 via la NVIDIA Integrate API (integrate.api.nvidia.com). Usa cuando el usuario pida hablar con GLM-5.2, NVIDIA Integrate, o un modelo razonador alternativo a los del perfil principal."
argument-hint: 'pregunta para GLM-5.2 | "explica el teorema de Bayes"'
allowed-tools: Bash, Read, Write
homepage: https://integrate.api.nvidia.com
author: local
license: MIT
user-invocable: true
---

# nvidia-glm

Skill que envuelve la NVIDIA Integrate API para chatear en streaming con `z-ai/glm-5.2`.

## Configuracion (CREDENTIALS)

La API key NO se guarda en el codigo. Se lee de la variable de entorno `NVAPI_KEY`
o de `~/.config/nvidia-glm/.env` (linea `NVAPI_KEY=nvapi-...`).

Para configurar, pide al usuario su key y escríbela con `>>` (append, NUNCA `>`)
en `~/.config/nvidia-glm/.env`:

```bash
mkdir -p ~/.config/nvidia-glm
printf 'NVAPI_KEY=nvapi-TU_KEY_AQUI\n' >> ~/.config/nvidia-glm/.env
```

## Uso

El script acepta el prompt por argumento o por stdin:

```bash
# Por argumento
python3 scripts/glm_chat.py "explica el teorema de Bayes en una linea"

# Por stdin (util para texto largo)
echo "resume esto: ..." | python3 scripts/glm_chat.py
```

La salida es streaming (token a token) en stdout. La API key se resuelve en runtime
desde el entorno o el `.env`; si falta, el script falla con un mensaje claro (exit 1).

## Verificacion

Tras configurar la key, un smoke test real:

```bash
python3 scripts/glm_chat.py "di hola en una palabra"
```

Debe imprimir la respuesta de GLM-5.2 y salir con codigo 0.
