#!/usr/bin/env bash
# Останавливаем выполнение скрипта при любой ошибке
set -o errexit

echo "--- Installing uv ---"
# Устанавливаем uv
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "--- Adding uv to PATH ---"
# Явно добавляем директорию с uv в системный PATH
export PATH="$HOME/.local/bin:$PATH"

echo "--- Installing dependencies ---"
# Используем uv напрямую для установки зависимостей
uv sync --no-build

echo "--- Running collectstatic ---"
# Используем uv напрямую для сборки статики
uv run python manage.py collectstatic --noinput

echo "--- Running migrations ---"
# Используем uv напрямую для применения миграций
uv run python manage.py migrate
