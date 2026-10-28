#!/usr/bin/env bash
# First boot on Oracle Ubuntu VM (cloud-init). Idempotent enough for retries.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
LOG=/var/log/reviewpilot-bootstrap.log
exec > >(tee -a "$LOG") 2>&1
echo "=== bootstrap $(date -Is) ==="

apt-get update -y
apt-get install -y git python3 python3-pip python3-venv postgresql postgresql-contrib redis-server \
  libpq-dev build-essential curl ca-certificates

systemctl enable --now postgresql redis-server

REPO="${REVIEWPILOT_REPO:-https://github.com/RoylestarIT/testbot.git}"
REF="${REVIEWPILOT_REF:-main}"
INSTALL_DIR=/opt/reviewpilot

if [[ ! -d "$INSTALL_DIR/.git" ]]; then
  git clone --depth 1 --branch "$REF" "$REPO" "$INSTALL_DIR"
fi
chown -R ubuntu:ubuntu "$INSTALL_DIR"

sudo -u ubuntu bash -lc "cd $INSTALL_DIR && python3 -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -r requirements.txt"

# systemd uses system python3; install deps for ubuntu user venv AND system for service
pip3 install -q -r "$INSTALL_DIR/requirements.txt" || pip3 install --break-system-packages -q -r "$INSTALL_DIR/requirements.txt"

touch "$INSTALL_DIR/.awaiting-env"
echo "Bootstrap done. Waiting for .env + finish script from deploy host." | tee /var/log/reviewpilot-bootstrap.done
