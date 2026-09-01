---
category: network
name: wireguard-vpn
description: Use for WireGuard VPN setup, double-hop, or iptables fix.
---

# WireGuard VPN

Set up and troubleshoot WireGuard VPN tunnels (server + client), including double-hop VPN (Oracle VPS → Mullvad), iptables forwarding, policy routing, and MTU optimization.

## Server setup (Linux VPS)

### 1. Install WireGuard
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install wireguard wireguard-tools
```

### 2. Generate keys
```bash
wg genkey | tee server_private.key | wg pubkey > server_public.key
wg genkey | tee client_private.key | wg pubkey > client_public.key
```

### 3. Server config (`/etc/wireguard/wg0.conf`)
```ini
[Interface]
Address = 10.66.66.1/24
ListenPort = 51820
PrivateKey = <server_private_key>
MTU = 1280
# IMPORTANT: use -I (insert) NOT -A (append) — rules must be BEFORE any REJECT all
PostUp = iptables -I FORWARD 3 -i wg0 -j ACCEPT
PostUp = iptables -I FORWARD 4 -o wg0 -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o <public_iface> -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -o wg0 -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o <public_iface> -j MASQUERADE

[Peer]
PublicKey = <client_public_key>
AllowedIPs = 10.66.66.2/32
```

### 4. Enable IP forwarding
```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
```

### 5. Start
```bash
sudo wg-quick up wg0
sudo systemctl enable wg-quick@wg0
```

## Client setup (Windows/Fireguard)

### Client config
```ini
[Interface]
PrivateKey = <client_private_key>
Address = 10.66.66.2/24
DNS = 1.1.1.1, 8.8.8.8
MTU = 1280

[Peer]
PublicKey = <server_public_key>
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = <server_ip>:51820
PersistentKeepalive = 25
```

### Install tunnel service (admin required)
```powershell
C:\Program Files\WireGuard\wireguard.exe /installtunnelservice C:\Users\<USER>\Downloads\wireguard-gio-pc.conf
```

## 🔥 Common Pitfall: Internet dies when activating tunnel

**Symptom**: Tunnel activates but internet is dead. Agent loses API connection.

**Cause**: iptables FORWARD has ACCEPT for wg0 **after** a REJECT all. Traffic arrives at VPS and gets rejected.

**Verification**: `sudo iptables -L FORWARD --line-numbers -v`

**Fix**: Move wg0 ACCEPT rules BEFORE the REJECT:
```bash
sudo iptables -D FORWARD -i wg0 -j ACCEPT
sudo iptables -D FORWARD -o wg0 -j ACCEPT
sudo iptables -I FORWARD 3 -i wg0 -j ACCEPT
sudo iptables -I FORWARD 4 -o wg0 -j ACCEPT
sudo sed -i 's/iptables -A FORWARD/iptables -I FORWARD 3/' /etc/wireguard/wg0.conf
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

## 🧅 Double VPN (Multi-hop: VPS → Mullvad)

Chain: `Your PC → VPS (wg0) → Mullvad (mullvad0) → Internet`

### Setup
1. Get Mullvad account (€5/mo, anonymous with Monero)
2. `curl -O https://raw.githubusercontent.com/mullvad/mullvad-wg.sh/main/mullvad-wg.sh`
3. `chmod +x mullvad-wg.sh && echo "<ACCOUNT>" | ./mullvad-wg.sh`
4. Create `/etc/wireguard/mullvad0.conf` with policy routing (Table=51820, route wg0 subnet traffic through Mullvad)
5. `sudo wg-quick up mullvad0`
6. Verify: `curl -s https://am.i.mullvad.net/connected`

### Notes
- Mullvad key needs ~60s to register on first connect
- Account must have balance
- When Mullvad is down, traffic falls back to VPS IP directly

## 📏 MTU
- VPS with 9000 MTU NIC: use 1280 on both wg0 and mullvad0
- Set via `MTU = 1280` under [Interface]

## Persistence
```bash
sudo apt install iptables-persistent
sudo iptables-save | sudo tee /etc/iptables/rules.v4
sudo systemctl enable wg-quick@wg0
```