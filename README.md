<div align="center">

# 🐙 Hermes Agent — Skill Collection

### La biblioteca de capacidades más completa para tu agente de IA

**251 skills · 34 categorías · listas para usar**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-251-brightgreen)](CATALOG.md)
[![Categories](https://img.shields.io/badge/categor%C3%ADas-34-blue)](CATALOG.md)

*Desarrollado y curado a lo largo de meses de evolución continua de un agente Hermes real.*

</div>

---

## 🚀 ¿Qué es esto?

Esta es una **colección curada y lista para usar** de skills para **[Hermes Agent](https://hermes-agent.nousresearch.com)** — el framework de agentes de IA de Nous Research.

Cada skill es un paquete autocontenido de conocimiento procedural: un `SKILL.md` que le enseña al agente **cómo** hacer algo (pasos exactos, comandos, pitfalls aprendidos, verificación), más los scripts y plantillas que lo acompañan.

> 💡 **Piensa en ello como el "cerebro operativo" de un agente.** No es código genérico: es la sabiduría acumulada de resolver problemas reales, una y otra vez, hasta que quedan perfectamente documentados.

---

## ✨ ¿Por qué es extraordinario?

| 🏆 Ventaja | Cómo se nota |
|-----------|-------------|
| **Sabiduría real** | Cada skill documenta *pitfalls* aprendidos con sangre — no teoría, sino qué rompe y cómo se arregla |
| **Verificación integrada** | Casi todas incluyen pasos de verificación para probar que algo *realmente* funcionó |
| **Autocontenidas** | Skills con sus propios scripts, plantillas y referencias — sin dependencias rotas |
| **De producción** | Nacidas de usar Hermes en el mundo real: devops, trading, MLOps, seguridad, investigación |
| **Evolutivas** | Un agente que se auto-mejora — estas skills representan ciclos reales de auto-evolución |

---

## 🗂️ Contenido por categoría

| Categoría | Qué cubre |
|-----------|-----------|
| 🤖 **Autonomous AI Agents** | Motores de autonomía, delegación a CLIs de código (Claude Code, Codex), multi-agente |
| ⚙️ **Engineering** | Diseño de módulos profundos, mejora de arquitectura, resolución de merge conflicts |
| 🧪 **MLOps** | Inferencia local, GGUF, LoRA, merge de checkpoints, VRAM, evaluación de modelos |
| 🔬 **Research** | Búsqueda profunda multi-paso, citas verificadas, arXiv, monitoreo de competencia |
| 🛠️ **Software Development** | TDD, debugging sistemático, code review, planificación, spikes |
| 📊 **Data Science** | Análisis interactivo, notebooks, extracción estructurada |
| 📈 **Trading** | Estrategias cuantitativas, backtesting, indicadores, markets de predicción |
| 🎨 **Creative** | Infografías, diagramas, video ASCII, música con IA, p5.js, ComfyUI |
| 🐙 **GitHub / DevOps** | PRs, issues, CI/CD, repos, merge — vía CLI `gh` |
| 📧 **Productividad** | Email, docs, hojas de cálculo, presentaciones, notas |
| 🔒 **Seguridad** | Hardening, red team, auditoría, OSINT, VPN, WireGuard |
| ✉️ **Comunicación** | Preferencias de respuesta, formato de cierre, extracción de tweets |
| ...y **22 más** | Ver [CATALOG.md](CATALOG.md) completo |

---

## 🧠 Lo que hace poderoso a un agente con estas skills

Un agente con esta biblioteca no "adivina" cómo hacer las cosas — **sabe**. En lugar de improvisar, carga la skill correcta y sigue un procedimiento probado que incluye:

1. **Cuándo usarla** — triggers claros en cada skill
2. **Pasos exactos** — comandos y rutas reales
3. **Pitfalls** — lo que falla y por qué
4. **Verificación** — cómo probar que funcionó
5. **Auto-mejora** — skills que se parchean a sí mismas cuando algo cambia

---

## 📥 Instalación

Copia las skills que necesites a tu carpeta de skills de Hermes:

```bash
# Windows (data dir real)
cp -r skills/* "$LOCALAPPDATA/hermes/skills/"

# macOS / Linux
cp -r skills/* ~/.hermes/skills/
```

O instala desde el hub oficial cuando la skill esté disponible:

```bash
hermes skills install <skill-name>
```

> 🔒 **Sanitizado:** este repo se publica sin ningún dato personal, credencial o
> ruta de máquina específica. Las rutas aparecen como `<USER>`, listas para que
> cada quien ponga las suyas.

---

## 🧭 Estructura del repo

```
skills/
├── <categoría>/
│   ├── <skill>/
│   │   ├── SKILL.md        # el conocimiento procedural (el corazón)
│   │   ├── scripts/        # scripts de soporte
│   │   └── references/     # documentos de referencia
│   └── ...
└── ...
```

---

## 📄 Documentación

- **[CATALOG.md](CATALOG.md)** — las **251 skills** completas con su descripción, agrupadas por categoría

---

## ⚖️ Licencia

MIT — úsalo, adáptalo, mejóralo. **Si una skill te ahorró horas, contribuye tus
mejoras de vuelta.** 🤝

---

<div align="center">

**Hecho con 🐙 + mucho trabajo de evolución continua**

*"Absorb what is useful, discard what is not, add what is uniquely your own."*
— Bruce Lee

</div>
