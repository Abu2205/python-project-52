#!/usr/bin/env bash
# Останавливаем выполнение скрипта при любой ошибке
set -o errexit

echo "--- Installing uv ---"
# Устанавливаем uv
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "--- Adding uv to PATH ---"
# Явно добавляем директорию с uv в системный PATH
export PATH="$HOME/.local/bin:$PATH"

# --- ВЫПОЛНЯЕМ ВСЕ ШАГИ СБОРКИ ПРЯМО ЗДЕСЬ ---

echo "--- Installing dependencies ---"
# Используем uv напрямую, но БЕЗ флага --no-build
uv sync

echo "--- Running collectstatic ---"
# Используем uv напрямую для сборки статики
uv run python manage.py collectstatic --noinput

echo "--- Running migrations ---"
# Используем uv напрямую для применения миграций
uv run python manage.py migrate