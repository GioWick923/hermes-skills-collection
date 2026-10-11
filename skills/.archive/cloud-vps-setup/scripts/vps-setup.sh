#!/usr/bin/env bash
# ============================================================
# vps-setup.sh — Setup completo de VPS gratuito (Oracle Free)
# Ejecutar UNA vez como ubuntu tras crear la instancia.
#   ssh -i ~/.ssh/id_ed25519_oracle ubuntu@IP_DEL_VPS
#   bash vps-setup.sh
# ============================================================
set -euo pipefail

echo "══════════════════════════════════════════════════"
echo "  VPS SETUP — Ubuntu 24.04 · Docker · Seguridad"
echo "══════════════════════════════════════════════════"

echo "→ [1/7] Actualizando sistema..."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

echo "→ [2/7] Instalando paquetes base..."
sudo apt-get install -y -qq \
    curl wget git unzip htop tmux \
    ufw fail2ban \
    ca-certificates gnupg lsb-release \
    python3 python3-pip \
    build-essential

echo "→ [3/7] Instalando Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -qq
sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io \
    docker-compose-plugin
sudo usermod -aG docker "$USER"

echo "→ [4/7] Configurando firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 8080/tcp
sudo ufw --force enable

echo "→ [5/7] Configurando fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null <<'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
EOF
sudo systemctl enable fail2ban --now

echo "→ [6/7] Creando swap de 4GB..."
if ! swapon --show | grep -q /swapfile; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

echo "→ [7/7] Verificando instalación..."
echo ""
echo "  ✔ Docker:      $(docker --version 2>/dev/null || echo 'falló')"
echo "  ✔ Compose:     $(docker compose version 2>/dev/null || echo 'falló')"
echo "  ✔ Firewall:    $(sudo ufw status | head -1)"
echo "  ✔ Fail2ban:    $(systemctl is-active fail2ban)"
echo "  ✔ Swap:        $(free -h | awk '/Swap/{print $2}')"
echo "  ✔ RAM:         $(free -h | awk '/Mem/{print $2}')"
echo "  ✔ CPU:         $(nproc) cores"
echo ""
echo "══════════════════════════════════════════════════"
echo "  ✅ VPS LISTO. Reinicia sesión para usar docker"
echo "  sin sudo:  exit && ssh -i ~/.ssh/id_ed25519_oracle ubuntu@IP"
echo "══════════════════════════════════════════════════"
