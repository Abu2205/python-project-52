#!/usr/bin/env bash
set -o errexit

echo "--- Installing uv ---"
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "--- Adding uv to PATH ---"
export PATH="$HOME/.local/bin:$PATH"


echo "--- Installing dependencies ---"
uv sync

echo "--- Running collectstatic ---"
uv run python manage.py collectstatic --noinput

echo "--- Running migrations ---"
uv run python manage.py migrate