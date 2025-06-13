.PHONY: install dev-setup lint test collectstatic migrate build render-start

# Установка зависимостей
install:
	uv sync --no-build

# Настройка для разработки
dev-setup:
	uv sync --dev
	uv run python manage.py migrate
	uv run python manage.py collectstatic --noinput

# Линтинг кода
lint:
	uv run flake8 .
	uv run isort --check-diff .

# Запуск тестов
test:
	uv run python manage.py test

# Сбор статических файлов
collectstatic:
	uv run python manage.py collectstatic --noinput

# Применение миграций
migrate:
	uv run python manage.py migrate

# Сборка проекта (для Render.com)
build:
	./build.sh

# Запуск для Render.com
render-start:
	uv run gunicorn task_manager.wsgi

# Локальный запуск для разработки
dev:
	uv run python manage.py runserver