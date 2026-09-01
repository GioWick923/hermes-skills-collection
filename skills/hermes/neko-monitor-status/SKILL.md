---
name: neko-monitor-status
description: Monitorea la salud del contenedor Neko Master.
category: hermes
version: 1.0.0
author: <USER>
license: MIT
metadata:
  hermes:
    tags: [monitor, docker, network, neko]
    related_skills: []
---

# Neko Monitor Status

## Purpose
Este skill verifica que el contenedor Docker `neko-master` está activo, comprueba su endpoint de salud y lo reinicia si está caído. Útil para CI o monitoreo periódico con cron de Hermes.

## Uso
```bash
hermes skill run neko-monitor-status          # solo comprobar salud
hermes skill run neko-monitor-status --restart # reiniciar si está unhealthy
```

## Implementación
El script principal está en `scripts/status.py`. Utiliza la CLI de Docker (debe estar instalada) para:
- **Pull** de la última imagen `foru17/neko-master` si no existe.
- **Garantizar** que un contenedor llamado `neko-master` está ejecutándose en el puerto configurado (por defecto 8080, sobrescribible con la variable `NEKO_PORT`).
- **Realizar** una petición HTTP `GET http://localhost:$NEKO_PORT/health` (o, si falla, inspeccionar logs) y generar un reporte Markdown.
- **Códigos de salida**: 0 = saludable, 1 = no saludable, 2 = contenedor ausente o error al iniciar.

## Verificación
- No modifica archivos; solo lecturas y una posible `docker start`.
- Imprime un reporte conciso en stdout y un JSON resumido en stderr (útil para pipelines CI).
