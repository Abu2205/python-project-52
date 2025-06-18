# test_pytest_wrapper.py
"""
Обертка для запуска Django тестов через pytest
"""
import os
import django
from django.conf import settings
from django.test.utils import get_runner

def test_run_django_tests():
    """Запускает все Django тесты через pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')
    django.setup()
    
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Запускаем только тесты из нашего приложения
    result = test_runner.run_tests(['task_manager_app'])
    
    # pytest ожидает исключение при неудаче
    if result:
        raise AssertionError(f"Django tests failed with {result} failures")