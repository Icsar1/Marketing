#!/usr/bin/env bash
set -euo pipefail

# Clean mirror deploy from this repo to server directory.
# Usage:
#   ./scripts/deploy_clean_to_vps.sh /root/opt/yandex_site_checker

TARGET_DIR="${1:-/root/opt/yandex_site_checker}"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "[ERROR] Target directory does not exist: $TARGET_DIR"
  echo "Create it first: mkdir -p $TARGET_DIR"
  exit 1
fi

echo "[INFO] Source: $SRC_DIR"
echo "[INFO] Target: $TARGET_DIR"

echo "[STEP] Stop old service if exists (ignore errors)"
systemctl stop yandex-site-checker 2>/dev/null || true
systemctl stop seo-analyzer 2>/dev/null || true

echo "[STEP] Mirror-copy project with delete (removes old files)"
rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  "$SRC_DIR/" "$TARGET_DIR/"

echo "[STEP] Rebuild venv and install deps"
python3 -m venv "$TARGET_DIR/.venv"
"$TARGET_DIR/.venv/bin/pip" install --upgrade pip
"$TARGET_DIR/.venv/bin/pip" install -r "$TARGET_DIR/requirements.txt"

echo "[DONE] Project mirrored to $TARGET_DIR"
echo "Run next: cd $TARGET_DIR && ls -la"
