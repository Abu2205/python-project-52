#!/usr/bin/env bash
# Скрипт сборки для Render.com

set -o errexit  # Остановить выполнение при ошибке

# Скачиваем uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Добавляем uv в PATH
export PATH="$HOME/.local/bin:$PATH"

# Установка зависимостей
make install

# Создание переводов
make makemessages

# Компиляция переводов
make compilemessages

# Сбор статических файлов
make collectstatic

# Применение миграций
make migrate