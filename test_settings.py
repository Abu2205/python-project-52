# test_settings.py
"""
Настройки Django для тестирования
"""
from task_manager.settings import *

# Переопределяем настройки для тестов
DEBUG = False

# Используем SQLite в памяти для быстрых тестов
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Отключаем миграции для ускорения тестов
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Упрощенная настройка паролей для тестов
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключаем логирование в тестах
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
}

# Отключаем Rollbar в тестах
ROLLBAR = None

# Отключаем кеширование
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Отключаем статические файлы
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Секретный ключ для тестов
SECRET_KEY = 'test-secret-key-only-for-testing'

# Ускоряем тесты
USE_TZ = False

# Отключаем интернационализацию в тестах для простоты
USE_I18N = False
USE_L10N = False