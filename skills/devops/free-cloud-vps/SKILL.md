---
name: free-cloud-vps
description: "VPS gratis (Oracle): cuenta, instancia, SSH, Docker."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [vps, oracle, free-tier, cloud, ssh, docker, ubuntu, provisioning]
    related_skills: [local-llm-operator-loop]
---

# Free Cloud VPS (Oracle Free Tier y alternativas)

Clase de trabajo: conseguir un servidor Linux virtual **gratis para siempre**
(Oracle Cloud Always Free) o barato, configurarlo (Docker + seguridad), y conectarse
por SSH. Incluye el laberinto real de la UI de Oracle (capacidad, subnet, IP pública).

## Cuándo usar
- El usuario pide un VPS gratuito (Europa/USA), quiere montar un servidor 24/7, o
  compara opciones (Daytona, Oracle, Hetzner, AWS).
- El usuario compartió un video/tutorial de "VPS gratis" y pregunta si es factible.

## Opciones (criterio honesto)
| Opción | Costo | Capacidad ARM | Cuándo |
|---|---|---|---|
| **Oracle Always Free ARM** | $0 | 2 OCPU + 12GB RAM + 200GB (reducido jun-2026, antes 4/24) | El mejor gratis — pero capacidad escasea |
| **Oracle x86 E2.1.Micro** | $0 | 1 OCPU + 1GB RAM + 50GB | Entra FÁCIL (sin cola) — para cosas ligeras |
| **Daytona (app.daytona.io)** | $200 crédito inicial | sandbox efímero | El "gratis infinito" del video es MITO — los créditos se agotan (~1.5 meses con 8GB) |
| **Hetzner** | ~€4/mes | 2 OCPU + 4GB | Si necesitas producción YA, sin juegos de capacidad |
| Google/AWS free | créditos temporales | limitado | Solo para probar |

## Oracle Free Tier — pasos (tu parte, requiere datos personales)
1. **Cuenta**: https://signup.cloud.oracle.com — tarjeta física Visa/MC (virtuales
   rechazadas), dirección EXACTA del banco (romanizada), sin VPN, IP de casa.
2. **Región (Home Region)**: NO cambia después. Europa→Frankfurt, USA→Phoenix/Ashburn.
3. **Instancia**: Compute → Instances → Create:
   - Imagen: Canonical Ubuntu 24.04 (NO Minimal — falta tooling)
   - Shape: Ampere → VM.Standard.A1.Flex → 2 OCPU + 12GB (máx gratis)
   - Storage: boot volume custom 200GB
   - SSH: pegar clave pública (generada local, ver abajo)
4. **Create** → esperar "Running" → copiar IP pública.

## SSH (preparado desde Hermes)
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_oracle -N "" -C "Gio-Oracle-FreeTier"
# pública en ~/.ssh/id_ed25519_oracle.pub → pegarla en Oracle
# conectar:
ssh -i ~/.ssh/id_ed25519_oracle ubuntu@IP_DEL_VPS
```

## Setup del VPS (script listo)
`workspace/scripts/vps-setup.sh` — instala Docker, compose, UFW, fail2ban, swap 4GB,
verifica todo. Ejecutar: `bash vps-setup.sh` como ubuntu.

## El laberinto de la UI de Oracle (pitfalls verificados)
- **"Select existing virtual cloud network" por defecto → bloqueado**: elegir
  **"Create new virtual cloud network"** + **"Create new public subnet"** (la subnet
  se crea sola; el subnet vacío de "Select existing" es el error clásico).
- **Public IPv4 = No (o switch gris)**: la IP pública solo se asigna en subnet pública.
  Si el switch está deshabilitado, la subnet es privada → volver a "Create new public subnet".
- **"Out of capacity for VM.Standard.A1.Flex in AD-1"**: normal — región llena.
  Solución: cambiar **Availability Domain** (AD-2/AD-3 — es el "edificio", distinto del
  Fault Domain que es el "piso"), o **cambiar de región**, o **reintentar** (madrugada/oleadas).
  Oracle sugiere explícitamente "Create instance without specifying a fault domain".
- **Fault domain ≠ Availability domain**: cambiar el piso no arregla el edificio lleno.
- **"Always Free Eligible" debe aparecer** en el shape — si no, cobra.
- Capacidad ARM se libera en oleadas: reintentar cada 10-15 min o cambiar AD/región.

## Verificación
- [ ] `ssh -i ~/.ssh/id_ed25519_oracle ubuntu@IP` entra
- [ ] `bash vps-setup.sh` → Docker, UFW, fail2ban OK
- [ ] IP pública visible en la consola tras "Running"

## Referencias
- `references/oracle-free-tier-2026.md` — detalles de la sesión (precios, regiones, errores)