---
name: free-vps-provisioning
description: "VPS gratis Oracle: cuenta, instancia ARM, SSH, setup."
version: 1.0.0
author: Gio + Hermes
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [vps, oracle-cloud, free-tier, arm, docker, ssh, ubuntu]
    related_skills: [docker, ssh]
---

# Free VPS Provisioning (Oracle Cloud Free Tier)

Clase de trabajo: conseguir un servidor Linux **gratis para siempre** (Always Free)
y dejarlo operativo. Oracle Cloud Free Tier es la opción real "gratis permanente"
(a diferencia de Daytona/sandboxes que dan crédito temporal).

## Cuándo usar
- El usuario quiere un VPS gratis / servidor 24/7 sin pagar.
- El usuario está creando cuenta o instancia en Oracle Cloud.
- Necesita conectar por SSH a una instancia nueva y dejarla lista (Docker, firewall).

## Lo que Oracle regala (Always Free, verificado jun-2026)
| Recurso | Cantidad |
|---|---|
| Instancia ARM Ampere A1 | **2 OCPUs + 12GB RAM** (reducido de 4/24 en jun-2026) |
| Boot volume | **200 GB** |
| Instancia x86 e2.micro | 1 opcional |
| Trial | $300 por 30 días (no obligatorio usar) |

## Requisitos para crear cuenta (barrera alta — preparar ANTES)
- Tarjeta **física** Visa/Mastercard (virtuales/prepago = rechazo alto).
- Dirección que coincida EXACTO con la del banco (en inglés/romanizado).
- Red de casa SIN VPN/proxy (IP debe coincidir con la dirección declarada).
- Email + teléfono reales. 1 cuenta por persona (duplicados = baneo).
- Si falla: esperar 24h, probar con tarjeta física, contactar soporte.

## Región (NO se puede cambiar después — decisión clave)
| Público | Región |
|---|---|
| Europa | Frankfurt (estable) |
| USA | Phoenix (más capacidad que Ashburn) |
| Asia | Tokyo/Osaka |

## Crear instancia (valores exactos)
- Image: **Canonical Ubuntu 24.04** (NO Minimal; NO 20.04 que es viejo).
- Shape: **Ampere → VM.Standard.A1.Flex** → 2 OCPU + 12GB.
- Boot volume: **200 GB** (activar "custom boot volume size").
- SSH: pegar clave pública. **La "Advanced options" se deja TODO default.**
- Los controles OCPU/RAM NO están en "Browse all shapes" — están en la pantalla
  principal de Create instance bajo el shape seleccionado. Si no aparecen editables,
  **crear igual con 1 OCPU/6GB** — se puede redimensionar después (5-10 min, reboot).
- Etiqueta: debe decir **"Always Free Eligible"** — si no, cobra.

## Claves SSH (generadas para Gio)
- Pública: `C:\Users\<USER>\.ssh\id_ed25519_oracle.pub` (pegar en Oracle)
- Privada: `C:\Users\<USER>\.ssh\id_ed25519_oracle` (nunca compartir)

## Conectar + setup (script ya preparado)
```bash
ssh -i ~/.ssh/id_ed25519_oracle ubuntu@IP_DEL_VPS
# copiar y ejecutar workspace/scripts/vps-setup.sh
```
El script instala: Docker + compose, UFW (SSH/80/443/3000/8080), fail2ban,
swap 4GB, y verifica. Ver también `templates/vps-setup.sh` (copia del script).

## Pitfalls
- **"Out of capacity"**: región saturada → esperar horas/días o cambiar región.
- **No crear recursos extra** (2ª instancia, volúmenes) → cobra.
- **Cuenta inactiva 30+ días** → puede suspenderse.
- **Free tier ARM reducido jun-2026**: si tienes instancia vieja 4/24, redimensionar a 2/12.
- **1/6 ya sirve** para Docker ligero, n8n, agentes; redimensionar después si hace falta.
- **No upgrade a PAYG** salvo que quieras alerta de $1 (recomendado si lo haces).

## Verificación
- [ ] Consola muestra la instancia "Running" con IP pública
- [ ] `ssh -i ~/.ssh/id_ed25519_oracle ubuntu@IP` entra
- [ ] `bash vps-setup.sh` termina con Docker, UFW y fail2ban OK
- [ ] `docker run hello-world` funciona sin sudo tras re-login
