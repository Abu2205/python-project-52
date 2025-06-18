# debug_test.py
import os
import sys

def test_debug_environment():
    print("=== DEBUG INFO ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Contents of current directory:")
    for item in os.listdir('.'):
        print(f"  {item}")
    print(f"manage.py exists: {os.path.exists('manage.py')}")
    print(f"task_manager exists: {os.path.exists('task_manager')}")
    
    # Попробуем найти manage.py
    for root, dirs, files in os.walk('.'):
        if 'manage.py' in files:
            print(f"Found manage.py in: {root}")
    
    assert True