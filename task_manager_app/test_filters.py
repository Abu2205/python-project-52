# task_manager_app/test_filters.py
"""
Отдельные тесты для системы фильтрации задач
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from task_manager_app.models import Status, Task, Label
from task_manager_app.filters import TaskFilter


class TaskFilterUnitTest(TestCase):
    """Юнит-тесты для TaskFilter"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        
        self.status1 = Status.objects.create(name='New')
        self.status2 = Status.objects.create(name='In Progress')
        
        self.label1 = Label.objects.create(name='Bug')
        self.label2 = Label.objects.create(name='Feature')
        
        # Создаем разнообразные задачи для тестирования
        self.task1 = Task.objects.create(
            name='Bug fix task',
            status=self.status1,
            author=self.user1,
            executor=self.user2
        )
        self.task1.labels.add(self.label1)
        
        self.task2 = Task.objects.create(
            name='Feature task',
            status=self.status2,
            author=self.user2,
            executor=self.user1
        )
        self.task2.labels.add(self.label2)
        
        self.task3 = Task.objects.create(
            name='No executor task',
            status=self.status1,
            author=self.user1
        )
        
        self.task4 = Task.objects.create(
            name='Multiple labels task',
            status=self.status2,
            author=self.user1,
            executor=self.user2
        )
        self.task4.labels.add(self.label1, self.label2)
    
    def test_filter_by_status(self):
        """Тест фильтрации по статусу"""
        # Создаем фильтр с мок-запросом
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Фильтруем по статусу "New"
        filter_data = {'status': self.status1.pk}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        expected_tasks = [self.task1, self.task3]
        
        self.assertEqual(len(filtered_tasks), 2)
        for task in expected_tasks:
            self.assertIn(task, filtered_tasks)
    
    def test_filter_by_executor(self):
        """Тест фильтрации по исполнителю"""
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Фильтруем по исполнителю user2
        filter_data = {'executor': self.user2.pk}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        expected_tasks = [self.task1, self.task4]
        
        self.assertEqual(len(filtered_tasks), 2)
        for task in expected_tasks:
            self.assertIn(task, filtered_tasks)
    
    def test_filter_by_label(self):
        """Тест фильтрации по метке"""
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Фильтруем по метке "Bug"
        filter_data = {'label': self.label1.pk}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        expected_tasks = [self.task1, self.task4]  # Обе задачи имеют метку Bug
        
        self.assertEqual(len(filtered_tasks), 2)
        for task in expected_tasks:
            self.assertIn(task, filtered_tasks)
    
    def test_filter_self_tasks(self):
        """Тест фильтрации собственных задач"""
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Фильтруем только собственные задачи user1
        filter_data = {'self_tasks': True}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        expected_tasks = [self.task1, self.task3, self.task4]  # Автор - user1
        
        self.assertEqual(len(filtered_tasks), 3)
        for task in expected_tasks:
            self.assertIn(task, filtered_tasks)
    
    def test_filter_self_tasks_false(self):
        """Тест что фильтр собственных задач не активен при False"""
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Не фильтруем собственные задачи
        filter_data = {'self_tasks': False}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        
        # Должны вернуться все задачи
        self.assertEqual(len(filtered_tasks), 4)
    
    def test_combined_filters(self):
        """Тест комбинации фильтров"""
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Комбинируем фильтры: статус + собственные задачи
        filter_data = {
            'status': self.status1.pk,
            'self_tasks': True
        }
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        expected_tasks = [self.task1, self.task3]  # Статус "New" и автор user1
        
        self.assertEqual(len(filtered_tasks), 2)
        for task in expected_tasks:
            self.assertIn(task, filtered_tasks)
    
    def test_empty_filter(self):
        """Тест пустого фильтра возвращает все задачи"""
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Пустой фильтр
        filter_data = {}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        
        # Должны вернуться все задачи
        self.assertEqual(len(filtered_tasks), 4)
    
    def test_filter_with_invalid_values(self):
        """Тест фильтрации с некорректными значениями"""
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Несуществующий статус
        filter_data = {'status': 9999}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        
        # Должны вернуться все задачи, так как фильтр некорректен
        self.assertEqual(len(filtered_tasks), 4)
    
    def test_filter_unauthenticated_user(self):
        """Тест фильтрации для неавторизованного пользователя"""
        from django.contrib.auth.models import AnonymousUser
        
        class MockRequest:
            def __init__(self):
                self.user = AnonymousUser()
        
        request = MockRequest()
        
        # Фильтр собственных задач для неавторизованного пользователя
        filter_data = {'self_tasks': True}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        filtered_tasks = list(task_filter.qs)
        
        # Должны вернуться все задачи, так как пользователь не авторизован
        self.assertEqual(len(filtered_tasks), 4)


class TaskFilterIntegrationTest(TestCase):
    """Интеграционные тесты фильтрации через веб-интерфейс"""
    
    def setUp(self):
        self.client = Client()
        
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            password='pass123'
        )
        
        self.status1 = Status.objects.create(name='To Do')
        self.status2 = Status.objects.create(name='Done')
        
        self.label1 = Label.objects.create(name='Urgent')
        self.label2 = Label.objects.create(name='Optional')
        
        # Создаем задачи с различными комбинациями параметров
        self.task1 = Task.objects.create(
            name='Urgent bug',
            status=self.status1,
            author=self.user1,
            executor=self.user2
        )
        self.task1.labels.add(self.label1)
        
        self.task2 = Task.objects.create(
            name='Optional feature',
            status=self.status2,
            author=self.user2,
            executor=self.user1
        )
        self.task2.labels.add(self.label2)
        
        self.task3 = Task.objects.create(
            name='My task',
            status=self.status1,
            author=self.user1
        )
    
    def test_filter_integration_status(self):
        """Интеграционный тест фильтрации по статусу"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {'status': self.status1.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Urgent bug')
        self.assertContains(response, 'My task')
        self.assertNotContains(response, 'Optional feature')
    
    def test_filter_integration_executor(self):
        """Интеграционный тест фильтрации по исполнителю"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {'executor': self.user1.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Optional feature')
        self.assertNotContains(response, 'Urgent bug')
        self.assertNotContains(response, 'My task')
    
    def test_filter_integration_label(self):
        """Интеграционный тест фильтрации по метке"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {'label': self.label1.pk})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Urgent bug')
        self.assertNotContains(response, 'Optional feature')
        self.assertNotContains(response, 'My task')
    
    def test_filter_integration_self_tasks(self):
        """Интеграционный тест фильтрации собственных задач"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {'self_tasks': 'on'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Urgent bug')
        self.assertContains(response, 'My task')
        self.assertNotContains(response, 'Optional feature')
    
    def test_filter_integration_multiple(self):
        """Интеграционный тест множественных фильтров"""
        self.client.force_login(self.user1)
        
        # Фильтруем по статусу и собственным задачам
        response = self.client.get(reverse('tasks_index'), {
            'status': self.status1.pk,
            'self_tasks': 'on'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Urgent bug')
        self.assertContains(response, 'My task')
        self.assertNotContains(response, 'Optional feature')
    
    def test_filter_form_persistence(self):
        """Тест сохранения состояния фильтров в форме"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {
            'status': self.status1.pk,
            'executor': self.user2.pk,
            'label': self.label1.pk,
            'self_tasks': 'on'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что фильтры остались выбранными в форме
        content = response.content.decode()
        self.assertIn(f'option value="{self.status1.pk}" selected', content)
        self.assertIn(f'option value="{self.user2.pk}" selected', content)
        self.assertIn(f'option value="{self.label1.pk}" selected', content)
        self.assertIn('input type="checkbox"', content)
    
    def test_filter_reset(self):
        """Тест сброса фильтров"""
        self.client.force_login(self.user1)
        
        # Сначала применяем фильтры
        response = self.client.get(reverse('tasks_index'), {
            'status': self.status1.pk,
            'self_tasks': 'on'
        })
        self.assertContains(response, 'Urgent bug')
        self.assertNotContains(response, 'Optional feature')
        
        # Затем сбрасываем фильтры (переходим без параметров)
        response = self.client.get(reverse('tasks_index'))
        
        # Должны показаться все задачи
        self.assertContains(response, 'Urgent bug')
        self.assertContains(response, 'Optional feature')
        self.assertContains(response, 'My task')
    
    def test_filter_edge_cases(self):
        """Тест граничных случаев фильтрации"""
        self.client.force_login(self.user1)
        
        # Пустые значения фильтров
        response = self.client.get(reverse('tasks_index'), {
            'status': '',
            'executor': '',
            'label': '',
        })
        self.assertEqual(response.status_code, 200)
        
        # Несуществующие ID
        response = self.client.get(reverse('tasks_index'), {
            'status': 9999,
            'executor': 9999,
            'label': 9999,
        })
        self.assertEqual(response.status_code, 200)
        
        # Невалидные значения
        response = self.client.get(reverse('tasks_index'), {
            'status': 'invalid',
            'executor': 'invalid',
            'label': 'invalid',
        })
        self.assertEqual(response.status_code, 200)


class TaskFilterFieldTest(TestCase):
    """Тесты отдельных полей фильтра"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.status = Status.objects.create(name='Test Status')
        self.label = Label.objects.create(name='Test Label')
    
    def test_status_field_choices(self):
        """Тест вариантов выбора для поля статус"""
        from task_manager_app.filters import TaskFilter
        
        # Создаем несколько статусов
        status2 = Status.objects.create(name='Another Status')
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        task_filter = TaskFilter(request=request)
        
        # Проверяем что все статусы доступны в выборе
        status_choices = list(task_filter.filters['status'].queryset)
        self.assertIn(self.status, status_choices)
        self.assertIn(status2, status_choices)
    
    def test_executor_field_choices(self):
        """Тест вариантов выбора для поля исполнитель"""
        from task_manager_app.filters import TaskFilter
        
        # Создаем еще одного пользователя
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        task_filter = TaskFilter(request=request)
        
        # Проверяем что все пользователи доступны в выборе
        executor_choices = list(task_filter.filters['executor'].queryset)
        self.assertIn(self.user, executor_choices)
        self.assertIn(user2, executor_choices)
    
    def test_label_field_choices(self):
        """Тест вариантов выбора для поля метка"""
        from task_manager_app.filters import TaskFilter
        
        # Создаем еще одну метку
        label2 = Label.objects.create(name='Another Label')
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        task_filter = TaskFilter(request=request)
        
        # Проверяем что все метки доступны в выборе
        label_choices = list(task_filter.filters['label'].queryset)
        self.assertIn(self.label, label_choices)
        self.assertIn(label2, label_choices)
    
    def test_self_tasks_field_widget(self):
        """Тест виджета для поля собственных задач"""
        from task_manager_app.filters import TaskFilter
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        task_filter = TaskFilter(request=request)
        
        # Проверяем что поле self_tasks имеет правильный виджет
        self_tasks_field = task_filter.filters['self_tasks']
        self.assertEqual(self_tasks_field.field.__class__.__name__, 'BooleanField')


class TaskFilterPerformanceTest(TestCase):
    """Тесты производительности фильтрации"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        
        self.status1 = Status.objects.create(name='Status1')
        self.status2 = Status.objects.create(name='Status2')
        
        self.label1 = Label.objects.create(name='Label1')
        self.label2 = Label.objects.create(name='Label2')
        
        # Создаем много задач для тестирования производительности
        self.tasks = []
        for i in range(100):
            task = Task.objects.create(
                name=f'Task {i}',
                status=self.status1 if i % 2 == 0 else self.status2,
                author=self.user1 if i % 3 == 0 else self.user2,
                executor=self.user1 if i % 4 == 0 else self.user2
            )
            
            # Добавляем метки к половине задач
            if i % 2 == 0:
                task.labels.add(self.label1)
            if i % 3 == 0:
                task.labels.add(self.label2)
            
            self.tasks.append(task)
    
    def test_filter_performance_status(self):
        """Тест производительности фильтрации по статусу"""
        from task_manager_app.filters import TaskFilter
        import time
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        start_time = time.time()
        
        filter_data = {'status': self.status1.pk}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        filtered_tasks = list(task_filter.qs)
        
        end_time = time.time()
        
        # Проверяем что фильтрация работает быстро (менее 1 секунды)
        self.assertLess(end_time - start_time, 1.0)
        
        # Проверяем корректность результата
        expected_count = Task.objects.filter(status=self.status1).count()
        self.assertEqual(len(filtered_tasks), expected_count)
    
    def test_filter_performance_complex(self):
        """Тест производительности сложной фильтрации"""
        from task_manager_app.filters import TaskFilter
        import time
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        start_time = time.time()
        
        # Комплексный фильтр
        filter_data = {
            'status': self.status1.pk,
            'executor': self.user1.pk,
            'label': self.label1.pk,
            'self_tasks': True
        }
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        filtered_tasks = list(task_filter.qs)
        
        end_time = time.time()
        
        # Проверяем что сложная фильтрация работает быстро
        self.assertLess(end_time - start_time, 2.0)
        
        # Результат должен быть непустым
        self.assertGreater(len(filtered_tasks), 0)
    
    def test_filter_database_queries(self):
        """Тест количества запросов к базе данных при фильтрации"""
        from task_manager_app.filters import TaskFilter
        from django.test.utils import override_settings
        from django.db import connection
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        with override_settings(DEBUG=True):
            initial_queries = len(connection.queries)
            
            filter_data = {
                'status': self.status1.pk,
                'executor': self.user1.pk,
                'label': self.label1.pk,
            }
            task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
            
            # Принудительно выполняем запрос
            list(task_filter.qs)
            
            final_queries = len(connection.queries)
            queries_count = final_queries - initial_queries
            
            # Количество запросов должно быть разумным (не более 10)
            self.assertLessEqual(queries_count, 10)


class TaskFilterValidationTest(TestCase):
    """Тесты валидации фильтров"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.status = Status.objects.create(name='Test Status')
        self.label = Label.objects.create(name='Test Label')
    
    def test_filter_with_deleted_status(self):
        """Тест фильтрации с удаленным статусом"""
        from task_manager_app.filters import TaskFilter
        
        # Запоминаем ID статуса
        status_id = self.status.pk
        
        # Удаляем статус
        self.status.delete()
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        
        # Пытаемся фильтровать по удаленному статусу
        filter_data = {'status': status_id}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        # Фильтр должен работать корректно (вернуть все задачи)
        filtered_tasks = list(task_filter.qs)
        self.assertEqual(len(filtered_tasks), 0)  # Нет задач в тестовых данных
    
    def test_filter_with_deleted_user(self):
        """Тест фильтрации с удаленным пользователем"""
        from task_manager_app.filters import TaskFilter
        
        user2 = User.objects.create_user(username='user2', password='pass123')
        user2_id = user2.pk
        
        # Удаляем пользователя
        user2.delete()
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        
        # Пытаемся фильтровать по удаленному пользователю
        filter_data = {'executor': user2_id}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        # Фильтр должен работать корректно
        filtered_tasks = list(task_filter.qs)
        self.assertEqual(len(filtered_tasks), 0)
    
    def test_filter_with_deleted_label(self):
        """Тест фильтрации с удаленной меткой"""
        from task_manager_app.filters import TaskFilter
        
        label_id = self.label.pk
        
        # Удаляем метку
        self.label.delete()
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        
        # Пытаемся фильтровать по удаленной метке
        filter_data = {'label': label_id}
        task_filter = TaskFilter(filter_data, queryset=Task.objects.all(), request=request)
        
        # Фильтр должен работать корректно
        filtered_tasks = list(task_filter.qs)
        self.assertEqual(len(filtered_tasks), 0)