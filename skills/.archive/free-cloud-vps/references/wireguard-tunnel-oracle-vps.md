# WireGuard VPN/Túnel en Oracle VPS

## Contexto
El VPS Oracle puede fungir como **VPN + túnel para disfrazar la IP de salida** usando WireGuard.
El servidor corre `wg0` con `AllowedIPs = 0.0.0.0/0, ::/0` (todo el tráfico del cliente
va por el túnel). Cliente Windows con WireGuard instalado.

## Verificación del túnel (desde Hermes)

### 1. Conectar al VPS
```bash
ssh -i ~/.ssh/oracle_key ubuntu@163.192.142.176
```

La clave real que funciona puede diferir de `id_ed25519_oracle` — probar varias:
- `~/.ssh/oracle_key` (más reciente, usuario Gio-Oracle-FreeTier)
- `~/.ssh/id_ed25519_oracle` (original)
- `~/Downloads/ssh-key-2026-08-21.key` (alternativa)

### 2. Verificar WireGuard en el servidor
```bash
sudo wg show
# → debe mostrar interface: wg0 + peer con allowed ips

sudo cat /etc/wireguard/wg0.conf
# → [Interface] con Address, ListenPort, PrivateKey, PostUp/PostDown iptables
# → [Peer] con PublicKey, AllowedIPs

sudo systemctl status wg-quick@wg0
# → debe estar active (running)
```

### 3. Verificar config del cliente Windows
- Ruta: `~/Downloads/wireguard-gio-pc.conf`
- Contenido típico:
  ```ini
  [Interface]
  PrivateKey = <cliente_priv>
  Address = 10.66.66.2/24
  DNS = 1.1.1.1, 8.8.8.8

  [Peer]
  PublicKey = <server_pub>
  AllowedIPs = 0.0.0.0/0, ::/0
  Endpoint = IP_VPS:51820
  PersistentKeepalive = 25
  ```

### 4. Verificar WireGuard en Windows
```bash
# Kernel WireGuard (drivers)
sc query WireGuard
# → debe mostrar RUNNING

# wg.exe (si está en PATH o en C:\Program Files\WireGuard\)
# o usar wireguard.exe con /installtunnelservice
```

### 5. Activar el túnel en Windows (admin required)
```powershell
# PowerShell como Administrador:
C:\Program Files\WireGuard\wireguard.exe /installtunnelservice C:\Users\<USER>\Downloads\wireguard-gio-pc.conf

# Luego iniciar el servicio:
Start-Service WireGuardTunnel$<nombre>
```

### 6. Guardar el hallazgo
Tras verificar/configurar, guardar en:
- **Memoria del agente**: `memory` con resumen de IP, puerto, claves públicas, estado
- **Obsidian vault**: nota en `20-Proyectos/VPS Gratis Oracle.md` con sección WireGuard

## Topología típica
```
Cliente Windows          VPS Oracle             Internet
10.66.66.2/24 ──wg:51820──> 10.66.66.1/24 ──enp0s5──> 🌐
                            iptables MASQUERADE
                            PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
                            PostUp = iptables -t nat -A POSTROUTING -o enp0s5 -j MASQUERADE
```

## Pitfalls
- **Permisos admin**: Windows no permite instalar servicios de túnel sin UAC elevado.
  `wireguard.exe /installtunnelservice` falla con "Acceso denegado" si no es admin.
- **Región del VPS**: Oracle VPS usa mx-queretaro-1 (México). Para cambiar endpoint
  a EE. UU., habría que destruir/crear en otra región (Home Region no cambia).
- **Claves SSH múltiples**: al crear varias llaves, la que pegaron en la consola de Oracle
  puede no ser la primera que se intenta. Verificar en `~/.ssh/` y en `~/Downloads/`.
- **IPTables**: los PostUp/PostDown rules son críticas para NAT. Si no están, el tráfico
  del cliente no sale a internet (el peer se conecta pero no hay forwarding).