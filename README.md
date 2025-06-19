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
```bash
make install
```

3. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

4. Настройте проект для разработки:
```bash
make dev-setup
```

5. Запустите сервер разработки:
```bash
make dev
```

Приложение будет доступно по адресу http://127.0.0.1:8000/

## Развертывание на Render.com

### Пошаговая инструкция:

1. **Подготовка репозитория:**
   - Загрузите код в GitHub репозиторий
   - Убедитесь, что файл `build.sh` имеет права на выполнение

2. **Создание Web Service на Render.com:**
   - Зайдите на [render.com](https://render.com)
   - Создайте новый "Web Service"
   - Подключите ваш GitHub репозиторий

3. **Настройки Build & Deploy:**
   - **Build Command:** `make build`
   - **Start Command:** `make render-start`
   - **Environment:** Python 3

4. **Создание базы данных PostgreSQL:**
   - Создайте новую PostgreSQL базу данных на Render.com
   - Скопируйте External Database URL

5. **Настройка переменных окружения:**
   ```
   SECRET_KEY=your-super-secret-key-here
   DEBUG=False
   DATABASE_URL=your-postgresql-database-url
   ```

6. **Деплой:**
   - Нажмите "Create Web Service"
   - Дождитесь завершения сборки и развертывания

## Доступные команды

```bash
make install          # Установка зависимостей
make dev-setup        # Настройка для разработки
make dev             # Запуск сервера разработки
make lint            # Проверка кода линтером
make test            # Запуск тестов
make test-coverage   # Запуск тестов с покрытием
make makemigrations    # Создание миграций
make migrate         # Применение миграций
make makemessages    # Создание файлов переводов
make compilemessages # Компиляция переводов
make createsuperuser # Создание суперпользователя
make loaddata        # Загрузка тестовых данных
make resetdb         # Сброс БД (только для разработки)
make build           # Сборка для продакшена
make render-start    # Запуск на Render.com
```

## Структура проекта

```
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
```

## Технологии

- **Backend:** Django 4.2+
- **Database:** PostgreSQL (продакшен), SQLite (разработка)
- **Deployment:** Render.com
- **Package Manager:** uv
- **Web Server:** Gunicorn
- **Static Files:** WhiteNoise

## Лицензия

Этот проект создан в образовательных целях в рамках курса Hexlet.