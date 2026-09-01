#!/usr/bin/env bash
# Pull the latest code and apply it on the production server.
# Run this from /var/www/natyabharathi after the initial setup in
# DEPLOYMENT.md has been done once.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Pulling latest code"
git pull origin main

echo "==> Installing dependencies"
.venv/bin/pip install -r requirements.txt

echo "==> Running migrations"
.venv/bin/python manage.py migrate --noinput

echo "==> Collecting static files"
.venv/bin/python manage.py collectstatic --noinput

echo "==> Restarting services"
sudo systemctl restart natyabharathi
sudo systemctl reload nginx

echo "==> Done. Check status with: sudo systemctl status natyabharathi"
