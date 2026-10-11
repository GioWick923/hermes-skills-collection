---
name: oci-cloud-vps
description: "Oracle Cloud VPS: free tier, API auth, VCN cleanup."
version: 1.0.0
author: Gio + Hermes
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [oracle, oci, vps, free-tier, cloud, vcn, api-key]
    related_skills: [local-model-install, local-gguf-deployment]
---

# Oracle Cloud VPS (OCI) — provisioning y administración

Administra el VPS gratuito de Oracle Cloud (Always Free): crear instancia, autenticar
con API key/SDK, y limpiar recursos (VCNs, subredes, IPs). Cubre el caso real de un
usuario que abrió instancias/IPs de más y necesita dejar "1 de cada cosa".

## Cuándo usar
- El usuario quiere un VPS gratis (Europa/USA) y eligió Oracle Cloud Free Tier.
- Hay que crear la cuenta, la instancia, o conectar por SSH.
- Hay que limpiar recursos duplicados (VCNs, IPs, VNICs) sin romper la instancia en uso.
- El usuario está atascado en la consola web y delegó la administración.

## Recursos Always Free (actualizado jun-2026)
- Instancia ARM Ampere A1: **2 OCPUs + 12 GB RAM** (¡se redujo de 4/24 en jun-2026!)
- Boot volume: **200 GB**
- Trial extra: $300 por 30 días (no obligatorio usar)
- Tarjeta física Visa/Mastercard obligatoria (virtuales/prepago = rechazo). No cobra en free tier.
- 1 cuenta por persona; inactiva 30+ días → suspensión.

## Crear cuenta (lo que el usuario debe hacer)
1. https://signup.cloud.oracle.com → Start for free
2. Dirección debe coincidir EXACTO con la del banco (en inglés/romanizado)
3. Sin VPN/proxy durante el registro (IP debe coincidir con la dirección)
4. **Home Region NO se puede cambiar** → Europa: Frankfurt; USA: Phoenix/Ashburn
5. Compute → Instances → Create Instance

## Crear instancia (valores exactos para no cobrar)
- Image: Canonical **Ubuntu 24.04**
- Shape: Ampere → **VM.Standard.A1.Flex** → **2 OCPU + 12 GB**
- Boot volume: **200 GB** (performance 120)
- SSH keys: pegar la pública SSH de `~/.ssh/`
- Etiqueta "Always Free Eligible" DEBE aparecer; si no, cobra.
- Error "Out of capacity" = región saturada → reintentar luego o cambiar región.

## Autenticación OCI (SDK Python) — pitfalls críticos

### Clave API: formato PEM vs SSH
- Oracle pide **formato PEM** (`-----BEGIN PUBLIC KEY-----`), NO `ssh-rsa AAAA...`.
- Generar par NUEVO en la PC cuando el usuario mezcló varias claves:
  ```bash
  cd ~/.oci && openssl genrsa -out nueva_api_key.pem 2048
  openssl rsa -in nueva_api_key.pem -pubout -out nueva_api_key_public.pem
  ```
  Copiar la pública a `~/Downloads/` (el usuario no siempre puede abrir `~/.oci`).

### Fingerprint: el gotcha del MD5 de vacío
- Fingerprint correcto = MD5 del DER de la pública:
  ```bash
  openssl pkey -pubin -in pub.pem -outform DER | openssl md5 -c   # método SPKI
  ```
- ⚠️ Si el comando falla silenciosamente, devuelve `d4:1d:8c:d9:8f:00:b2:04:e9:80:09:98:ec:f8:42:7e`
  que es literalmente el **MD5 de una cadena vacía** — señal de que la pública no parseó.
  No confundirlo con un fingerprint real.
- El fingerprint que Oracle muestra en el config preview es el de la clave QUE SUBIÓ;
  si el usuario generó varias, verificar cuál pública corresponde a la privada guardada.

### Config y SDK
```bash
cat > ~/.oci/config <<'EOF'
[DEFAULT]
user=ocid1.user.oc1..XXXX
fingerprint=XX:XX:XX:...
tenancy=ocid1.tenancy.oc1..YYYY
region=mx-queretaro-1
key_file=C:/Users/<USER>/.oci/nueva_api_key.pem
EOF
```
- En Windows, `key_file` con forward slashes funciona.
- Convertir la privada a LF (quitar `\r`) si hay problemas de lectura.
- Autenticación de prueba: `oci.identity.IdentityClient(config).list_region_subscriptions(tenancy)`
  funciona aunque `get_tenancy` o `list_instances` devuelvan 401 por permisos de endpoint.
- 401 en compute pero OK en identity = tema de permisos/política, no de clave.

## Limpieza de recursos (VCNs duplicadas, IPs extra)

### Orden de borrado de una VCN (¡crítico!)
1. **Vaciar route tables** con `UpdateRouteTableDetails(route_rules=[])` (no filtrar — vaciar).
   El IG da `409 Conflict` mientras una route rule lo referencie.
2. **Eliminar Internet Gateway** → luego subredes → route tables → security lists → DHCP → VCN.
3. Esperar 3-5s entre pasos (propagación).
4. Si `delete_vcn` da `IncorrectState`, falta un componente (IG es el típico oculto).

### IPs públicas
- `list_public_ips("REGION", tenancy)` → eliminar las que no están asociadas a la VNIC en uso.
- La IP de la instancia puede NO aparecer en esa lista (efímera asignada en la consola) —
  no borrar a ciegas; verificar con SSH que la conexión sigue viva tras limpiar.

### Verificación final
- 1 VCN, 1 instancia RUNNING, 1 VNIC principal, 1 IP pública.
- `ssh -i ~/.ssh/oracle_key ubuntu@IP "hostname"` debe responder.

## Pitfalls
- No borrar la VCN que contiene la subnet de la instancia (verificar `list_subnets` por vcn_id).
- VNIC secundaria: `detach_vnic` la desasocia; el get_vnic posterior da 404 = correcto (destruida).
- El script de setup del VPS vive en `workspace/scripts/vps-setup.sh` (Docker+UFW+fail2ban+swap).
- Nota del vault: `20-Proyectos/VPS Gratis Oracle.md`.

## Verificación
- [ ] `oci` SDK importable y config carga (`oci.config.from_file`)
- [ ] `list_region_subscriptions` OK → credenciales válidas
- [ ] SSH a la IP pública responde
- [ ] Tras limpieza: 1 VCN + 1 instancia + 1 VNIC
