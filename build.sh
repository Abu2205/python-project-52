#!/usr/bin/env bash
# Останавливаем выполнение скрипта при любой ошибке
set -o errexit

echo "--- Installing uv ---"
# Устанавливаем uv, как и раньше
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "--- Adding uv to PATH ---"
# Явно добавляем директорию с uv в системный PATH.
# Это более надежный способ, чем 'source'.
export PATH="$HOME/.local/bin:$PATH"

echo "--- Running build steps ---"
# Теперь вызываем ваши команды make. Они смогут найти 'uv'.
make install
make collectstatic
make migrate
