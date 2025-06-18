.PHONY: install dev-setup lint test collectstatic migrate build render-start dev makemessages compilemessages test-coverage createsuperuser loaddata makemigrations resetdb

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
	uv run python -m pytest

# Запуск тестов Django стиле (альтернативный способ)
test-django:
	uv run python manage.py test

# Запуск тестов с покрытием (если установлен coverage)
test-coverage:
	uv run coverage run --source='.' -m pytest
	uv run coverage report

# Создание суперпользователя
createsuperuser:
	uv run python manage.py createsuperuser

# Загрузка тестовых данных
loaddata:
	uv run python manage.py loaddata users.json statuses.json tasks.json

# Создание миграций
makemigrations:
	uv run python manage.py makemigrations

# Сброс базы данных (только для разработки)
resetdb:
	rm -f db.sqlite3
	make migrate
	make loaddata

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

# Создание переводов
makemessages:
	uv run python manage.py makemessages -l ru

# Компиляция переводов
compilemessages:
	uv run python manage.py compilemessages

	# Запуск тестов с pytest
test:
	uv run pytest

# Запуск тестов Django
test-django:
	uv run python manage.py test

# Запуск тестов с покрытием
test-coverage:
	uv run pytest --cov=task_manager_app --cov-report=html --cov-report=term

# Запуск только быстрых тестов
test-fast:
	uv run pytest -m "not slow"

# Запуск только тестов фильтрации
test-filters:
	uv run pytest -m filter