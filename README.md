### Hexlet tests and linter status:
[![Actions Status](https://github.com/Abu2205/python-project-52/actions/workflows/hexlet-check.yml)](https://github.com/Abu2205/python-project-52/actions)

### SonarQube badge
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Abu2205_python-project-52&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Abu2205_python-project-52)

# Hexlet Code - Task Manager

Django приложение для управления задачами, разработанное в рамках курса Hexlet.

## Описание

Task Manager - это веб-приложение на Django для управления задачами и проектами. Приложение развернуто на платформе Render.com и использует PostgreSQL в качестве базы данных.

## Демо

🚀 **[Посмотреть живое приложение](https://your-app-name.onrender.com)**

## Требования

- Python 3.10+
- uv (Python package manager)

## Локальная установка и запуск

1. Склонируйте репозиторий:
git clone https://github.com/Abu2205/python-project-52.git
cd hexlet-code

2. Установите зависимости:
make install

3. Запустите сервер разработки:

make dev

Приложение будет доступно по адресу http://127.0.0.1:8000/


## Структура проекта

hexlet-code/
├── task_manager/           # Основные настройки Django
│   ├── settings.py         # Конфигурация Django
│   ├── urls.py            # URL маршрутизация
│   └── wsgi.py            # WSGI конфигурация
├── task_manager_app/       # Основное приложение
│   ├── views.py           # Представления
│   ├── urls.py            # URL маршруты приложения
│   └── models.py          # Модели данных
├── templates/              # HTML шаблоны
├── build.sh               # Скрипт сборки для Render.com
├── Makefile              # Команды для разработки
├── pyproject.toml        # Конфигурация проекта и зависимости
└── README.md             # Документация
