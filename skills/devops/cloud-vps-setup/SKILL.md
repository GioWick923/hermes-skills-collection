---
name: cloud-vps-setup
description: "VPS gratis: Oracle Free Tier, claves, OCI CLI, setup."
version: 1.0.0
author: Gio + Hermes
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [vps, oracle, cloud, free-tier, oci, ssh, docker]
    related_skills: [agent-api-gateway-patterns, dsh-ornith-bridge]
---

# Cloud VPS Setup — Oracle Free Tier y similares

Clase de trabajo: montar un VPS (servidor virtual privado) **gratis** en la nube,
conectarse por SSH y dejar el servidor listo (Docker + seguridad).

## Cuándo usar
- El usuario quiere un VPS gratis (USA/Europa/global) para agentes 24/7, servicios, Docker.
- El usuario comparte un video/tutorial de "VPS gratis" (Daytona, Oracle, etc.) y pregunta si es factible.
- Montar/arreglar la conexión SSH o el OCI CLI con una cuenta Oracle ya creada.

## Comparativa de opciones (2026)
| Opción | Costo | Notas |
|---|---|---|
| **Oracle Cloud Free Tier** | **Gratis para siempre** | 2 OCPU ARM + 12GB RAM + 200GB (reducido jun-2026 desde 4/24). El mejor gratis real. |
| Daytona (app.daytona.io) | $200 crédito inicial | Pay-as-you-go, NO infinito. Sandbox efímero. |
| Hetzner | ~€4/mes | Barato y serio en Europa (no gratis). |

## Oracle Free Tier — proceso completo

### 1. Crear cuenta (el usuario lo hace — pide tarjeta física)
- https://signup.cloud.oracle.com → "Start for free"
- **Tarjeta física Visa/Mastercard** (virtuales/prepago = rechazo alto). Solo verificación, no cobra.
- **Dirección debe coincidir EXACTO** con la del banco (en inglés/romanizado).
- **Sin VPN/proxy** al registrarse (el IP debe coincidir con la dirección).
- **Elegir Home Region con cuidado — NO se puede cambiar después**: Europa→Frankfurt, USA→Phoenix, Asia→Tokyo.
- 1 cuenta por persona. Cuenta inactiva 30+ días → puede suspenderse.

### 2. Crear instancia (el usuario lo hace — 5 clics)
- Compute → Instances → Create Instance
- **Image**: Canonical Ubuntu 24.04
- **Shape**: Ampere → VM.Standard.A1.Flex → **2 OCPU + 12GB RAM** (límite gratis; 4/24 ya no existe)
- **Boot volume**: 200 GB (máx gratis)
- **SSH keys**: pegar clave pública (ver abajo)
- **Buscar la etiqueta "Always Free Eligible"** — si no aparece, va a cobrar.
- Error "Out of capacity" → esperar o cambiar región.

### 3. Claves SSH (las genera Hermes)
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_oracle -N "" -C "Gio-Oracle"
# Pública en ~/.ssh/id_ed25519_oracle.pub → pegar en Oracle
# Conectar: ssh -i ~/.ssh/id_ed25519_oracle ubuntu@IP_PUBLICA
```

### 4. OCI CLI / SDK (para automatizar desde Hermes)
```bash
pip install oci-cli   # o usar el módulo `oci` en python
```
Config en `~/.oci/config`:
```ini
[DEFAULT]
user=ocid1.user.oc1..<USER_OCID>
fingerprint=<FINGERPRINT>
tenancy=ocid1.tenancy.oc1..<TENANCY_OCID>
region=mx-queretaro-1
key_file=C:/Users/<USER>/.oci/<clave>.pem
```
- **User OCID**: consola → avatar → My profile → OCID visible.
- **Tenancy OCID**: NUNCA buscar en "My profile". Ir a **Identity → Compartments** → el compartimiento raíz (root) tiene el MISMO OCID que el tenancy. (Lección aprendida: no existe endpoint de UI directo que lo muestre fácil; el root compartment es el atajo.)
- **API key**: My profile → API keys → Add API key → **"Upload public key file"** (PEGAR texto da "PEM INVALID" por caracteres invisibles). Al subir, muestra "Configuration File Preview" con user/fingerprint/tenancy/region — pedir ese texto al usuario.

### 5. Pitfalls críticos del OCI CLI (lecciones de sesión real)
- **Fingerprint**: calcular con `openssl pkey -pubin -in <pub.pem> -outform DER | openssl md5 -c` desde la clave **pública**. ⚠️ Si el archivo PEM tiene CRLF (Windows), `openssl pkey -pubin` puede fallar silenciosamente y devolver el MD5 de cadena vacía (`d4:1d:8c:d9:8f:00:b2:04:e9:80:09:98:ec:f8:42:7e`) — ese hash es EL MISMO para cualquier archivo vacío, es señal de error de lectura, no fingerprint real. Convertir a LF: `sed -i 's/\r$//' archivo.pem`.
- **Verificar que la privada corresponde a la pública**: `openssl pkey -in <privada.pem> -pubout -outform DER | openssl md5 -c` debe dar el MISMO fingerprint que el config preview de Oracle. Si difiere → tienes claves de pares distintos (muy común cuando el usuario genera el par 2 veces).
- **Error 401 NotAuthenticated en get_tenancy pero list_region_subscriptions OK**: la clave es válida; el problema es de permisos de endpoint (Free Tier), no de credenciales. Probar con `list_region_subscriptions` primero para validar auth.
- **list_instances 401 en Free Tier**: puede fallar por permisos aunque la auth base funcione. No es fallo de la clave.
- **Asignar IP pública**: en la consola web es lo más fiable (la API a veces da 401 en Free Tier): instancia → Attached VNICs → VNIC → IPv4 addresses → Edit → "Ephemeral public IP" → Update. Ephemeral = gratis (cambia al reiniciar); Reserved = de pago.

## Setup del servidor (una vez conectado)
Script listo: `workspace/scripts/vps-setup.sh` — instala Docker, docker-compose, UFW (firewall), fail2ban (anti brute-force SSH), swap 4GB, y verifica.

```bash
ssh -i ~/.ssh/id_ed25519_oracle ubuntu@IP_PUBLICA
# copiar/pegar el contenido de vps-setup.sh → bash vps-setup.sh
```

## Verificación
- [ ] `ssh -i <clave> ubuntu@IP` conecta
- [ ] Fingerprint local == fingerprint del config preview de Oracle
- [ ] `python -c "import oci; ... list_region_subscriptions"` autentica
- [ ] `bash vps-setup.sh` termina con Docker/UFW/fail2ban OK
