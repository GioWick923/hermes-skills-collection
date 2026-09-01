---
name: hermes-security-audit
description: Audita configuración, skills, MCP y cron de Hermes.
category: hermes
version: 1.0.0
author: <USER>
license: MIT
metadata:
  hermes:
    tags: [security, audit, hermes]
    related_skills: []
---

# Hermes Security Audit

## Propósito
Este skill verifica el estado de seguridad de su instalación de Hermes, cubriendo:

1. **Configuración** – archivos `config.yaml` y `.env` en `$HERMES_HOME`.
2. **Skills** – front‑matter, uso de comandos de alto riesgo, servidores MCP asociados.
3. **MCP** – servidores configurados, disponibilidad y versiones.
4. **Cron** – trabajos programados que ejecutan scripts, validando existencia del script y entorno.

Genera un informe en **Markdown** y opcionalmente **JSON** con severidad `critical/high/medium/low/info` y un `exitCode` (0 = OK, 1 = HIGH, 2 = CRITICAL).

## Uso
```bash
hermes skill run hermes-security-audit   # ejecuta la auditoría y muestra el informe
hermes skill exec hermes-security-audit --json > audit.json   # guarda JSON
```

## Implementación
El skill consta de:
- `audit.py` – script Python autosuficiente que realiza todas las comprobaciones.
- `SKILL.md` – este archivo con metadatos.

## Verificación
- El script se ejecuta sin modificar ningún archivo.
- El informe incluye enlaces a los archivos problemáticos.
- Se ejecuta en modo lectura; no se realizan cambios automáticos.

## Notas de desarrollo

## When to Use
- Necesitas validar que tu entorno Hermes no contiene secretos en `.env`.
- Quieres detectar comandos peligrosos dentro de tus skills.
- Requieres comprobar la salud de los servidores MCP y los trabajos cron.
- Buscas un informe rápido en CI con código de salida que indique gravedad.
- Requiere `PyYAML` (ya disponible en el entorno Hermes).
- Detecta secretos mediante expresiones regulares sencillas.
- Usa `hermes mcp list` y `hermes cron list` para obtener datos en tiempo real.

## Estructura del skill
```
hermes-security-audit/
├── SKILL.md          # este archivo
└── audit.py          # script de auditoría (se creará al ejecutar la skill)
```

## Próximos pasos
Una vez creado el skill, la primera ejecución mostrará una plantilla de informe vacía y un mensaje de "no se han detectado problemas".
