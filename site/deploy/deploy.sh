#!/usr/bin/env bash
# F2O site — idempotent redeploy (static; no service). Auth via the `wip` SSH
# alias only — no credentials in this file.
set -euo pipefail

HOST="${DEPLOY_SSH_HOST:-wip}"
REMOTE_DIR="/opt/f2o"
HERE="$(cd "$(dirname "$0")/.." && pwd)"   # -> site/

echo "==> ssh check"; ssh -o BatchMode=yes "$HOST" true

echo "==> sync site -> $REMOTE_DIR/app"
rsync -az --delete --exclude 'deploy' -e ssh "$HERE/" "$HOST:$REMOTE_DIR/app/"

echo "==> sync deploy assets (nginx conf reference copy)"
rsync -az -e ssh "$HERE/deploy/" "$HOST:$REMOTE_DIR/deploy/"

echo "==> health"
curl -fsSI https://f2o.workinproblem.com/ | head -1
echo "==> done"
