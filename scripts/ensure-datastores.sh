#!/usr/bin/env bash
# Start Redis + PostgreSQL when systemd is unavailable (Cloud Agent VM).
set -euo pipefail

if ! redis-cli ping >/dev/null 2>&1; then
  redis-server --daemonize yes --dir /tmp --logfile /tmp/redis-reviewpilot.log
  echo "Redis started"
fi

if command -v pg_ctlcluster >/dev/null 2>&1; then
  if ! pg_lsclusters 2>/dev/null | awk '{print $4}' | grep -qx online; then
    sudo pg_ctlcluster 16 main start || sudo pg_ctlcluster "$(pg_lsclusters -h | awk 'NR==2{print $1}')" main start
    echo "PostgreSQL started"
  fi
fi
