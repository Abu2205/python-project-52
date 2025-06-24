.PHONY: install dev-setup lint test collectstatic migrate build render-start dev makemessages compilemessages

# Установка зависимостей
install:
	uv sync

# Настройка для разработки
dev-setup:
	uv sync --dev
	uv run python manage.py migrate
	uv run python manage.py collectstatic --noinput

# Линтинг и тесты
lint:
	uv run ruff check .
	uv run ruff format --check .
test:
	uv run python -m pytest

# Команды для Django
collectstatic:
	uv run python manage.py collectstatic --noinput
migrate:
	uv run python manage.py migrate

# Команда сборки для Render.com
build:
	./build.sh

# Команда запуска для Render.com
render-start:
	gunicorn task_manager.wsgi --log-file -

# Локальный запуск для разработки
dev:
	uv run python manage.py runserver

# Команды для переводов
makemessages:
	uv run python manage.py makemessages -l ru
compilemessages:
	uv run python manage.py compilemessages
