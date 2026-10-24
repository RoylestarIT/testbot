#!/usr/bin/env bash
# Provision Oracle Always Free VM and migrate bot from this machine (run where .env exists).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TF_DIR="$ROOT/deploy/oracle/terraform"

: "${OCI_SSH_PRIVATE_KEY:?Set OCI_SSH_PRIVATE_KEY path or export before running}"
SSH_USER="${OCI_SSH_USER:-ubuntu}"
SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -i "$OCI_SSH_PRIVATE_KEY")

if [[ ! -f "$TF_DIR/terraform.tfvars" ]]; then
  echo "Copy deploy/oracle/terraform/terraform.tfvars.example → terraform.tfvars and fill OCI fields."
  exit 1
fi

TF="${TERRAFORM_BIN:-}"
if [[ -z "$TF" ]]; then
  if command -v terraform >/dev/null; then TF=terraform
  elif [[ -x "$ROOT/.bin/terraform" ]]; then TF="$ROOT/.bin/terraform"
  else echo "Install terraform or set TERRAFORM_BIN"; exit 1; fi
fi

echo "=== Terraform apply (Oracle A1) ==="
(cd "$TF_DIR" && "$TF" init -input=false && "$TF" apply -input=false -auto-approve)

IP="$(cd "$TF_DIR" && "$TF" output -raw public_ip)"
echo "Instance IP: $IP"

echo "=== Waiting for SSH ==="
for i in $(seq 1 60); do
  if ssh "${SSH_OPTS[@]}" "$SSH_USER@$IP" true 2>/dev/null; then
    break
  fi
  sleep 10
done
ssh "${SSH_OPTS[@]}" "$SSH_USER@$IP" true

echo "=== Waiting for cloud-init bootstrap ==="
for i in $(seq 1 60); do
  if ssh "${SSH_OPTS[@]}" "$SSH_USER@$IP" test -f /var/log/reviewpilot-bootstrap.done; then
    break
  fi
  sleep 10
done

echo "=== Backup current DB ==="
BACKUP="$ROOT/backups/oracle-migrate-$(date +%Y%m%d-%H%M%S).sql.gz"
bash "$ROOT/scripts/backup-db.sh" "$(dirname "$BACKUP")"
LATEST="$(ls -t "$ROOT/backups"/reviewpilot-*.sql.gz 2>/dev/null | head -1)"
[[ -n "$LATEST" ]] || { echo "No PostgreSQL backup found"; exit 1; }

echo "=== Copy .env and database ==="
scp "${SSH_OPTS[@]}" "$ROOT/.env" "$SSH_USER@$IP:/opt/reviewpilot/.env"
scp "${SSH_OPTS[@]}" "$LATEST" "$SSH_USER@$IP:/tmp/reviewpilot-migrate.sql.gz"
scp "${SSH_OPTS[@]}" "$ROOT/scripts/oracle-remote-finish.sh" "$ROOT/scripts/setup-postgres-from-env.sh" \
  "$ROOT/scripts/install-systemd.sh" "$SSH_USER@$IP:/opt/reviewpilot/scripts/"
scp "${SSH_OPTS[@]}" "$ROOT/deploy/reviewpilot.service" "$SSH_USER@$IP:/opt/reviewpilot/deploy/reviewpilot.service"

ssh "${SSH_OPTS[@]}" "$SSH_USER@$IP" "cd /opt/reviewpilot && sudo bash scripts/oracle-remote-finish.sh"

echo "=== Oracle health ==="
ssh "${SSH_OPTS[@]}" "$SSH_USER@$IP" "curl -sf localhost:8081/health"

echo ""
echo "Done. Stop the OLD bot (Cloud Agent VM) so only one process uses BOT_TOKEN:"
echo "  pkill -f 'python3 -m app.main'"
echo "SSH: ssh -i $OCI_SSH_PRIVATE_KEY $SSH_USER@$IP"
echo "Logs: ssh … 'journalctl -u reviewpilot -f'"
