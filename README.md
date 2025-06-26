# Менеджер задач

[![Hexlet Check](https://github.com/Abu2205/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Abu2205/python-project-52/actions/workflows/hexlet-check.yml)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Abu2205_python-project-52&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Abu2205_python-project-52)

"Менеджер задач" — это веб-приложение для управления задачами, созданное на Django. Оно позволяет пользователям регистрироваться, управлять задачами, назначать им статусы, исполнителей и метки.

## Ссылка на задеплоенное приложение

[https://python-project-52-v8fi.onrender.com](https://python-project-52-v8fi.onrender.com)

## Ключевые возможности

- **Аутентификация:** Регистрация, вход и выход пользователей.
- **Управление пользователями:** Просмотр списка пользователей, редактирование и удаление своего профиля.
- **Управление задачами:** Создание, редактирование, просмотр и удаление задач.
- **Статусы и метки:** Создание, редактирование и удаление статусов и меток для задач.
- **Фильтрация:** Возможность фильтровать задачи по статусу, исполнителю и меткам.

## Технологии

- **Backend:** Python, Django
- **Frontend:** HTML, Bootstrap 5
- **База данных:** PostgreSQL (в продакшене), SQLite3 (в разработке)
- **Деплой:** Render
- **CI/CD:** GitHub Actions, SonarQube

## Структура проекта


├── task_manager/
│   ├── settings.py         # Главные настройки проекта
│   ├── urls.py             # Главный файл URL-маршрутизации
│   ├── wsgi.py
│   ├── asgi.py
│   ├── task_manager_app/   # Django-приложение
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── task_manager_app/
│   │   ├── init.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── templates/            # Общие шаблоны (base.html, index.html)
├── Makefile                # Команды для управления проектом
├── manage.py               # Утилита для управления Django
├── pyproject.toml          # Зависимости проекта для uv/Poetry
└── README.md


## Установка и запуск

1.  **Клонировать репозиторий:**
    git clone [https://github.com/Abu2205/python-project-52.git](https://github.com/Abu2205/python-project-52.git)
    cd python-project-52


2.  **Создать и активировать виртуальное окружение:**
    python3 -m venv .venv
    source .venv/bin/activate


3.  **Установить зависимости с помощью `uv`:**
    pip install uv
    uv sync


4.  **Применить миграции:**
    python manage.py migrate


5.  **Запустить сервер для разработки:**
    python manage.py runserver
    ```

Приложение будет доступно по адресу `http://127.0.0.1:8000/`.