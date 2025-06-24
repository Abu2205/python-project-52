"""
Тесты для Django приложения Task Manager
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Status, Task, Label


class BaseTestCase(TestCase):
    """Базовый класс для тестов"""
    
    def setUp(self):
        self.client = Client()
        
        self.user1 = User.objects.create_user(
            username='testuser1',
            first_name='Test',
            last_name='User1',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            first_name='Test',
            last_name='User2',
            password='testpass123'
        )
        
        self.status1 = Status.objects.create(name='New')
        self.status2 = Status.objects.create(name='In Progress')
        
        self.label1 = Label.objects.create(name='Bug')
        self.label2 = Label.objects.create(name='Feature')


class IndexViewTest(BaseTestCase):
    """Тесты главной страницы"""
    
    def test_index_view(self):
        """Тест отображения главной страницы"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Привет от Хекслета!')


class UserViewsTest(BaseTestCase):
    """Тесты для представлений пользователей"""
    
    def test_users_list_view(self):
        """Тест списка пользователей"""
        response = self.client.get(reverse('users_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.username)
    
    def test_user_create_view_get(self):
        """Тест GET запроса формы регистрации"""
        response = self.client.get(reverse('user_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_create_view_post_success(self):
        """Тест успешной регистрации пользователя"""
        data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
        }
        response = self.client.post(reverse('user_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class AuthViewsTest(BaseTestCase):
    """Тесты аутентификации"""
    
    def test_login_view_get(self):
        """Тест GET запроса страницы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view_post_success(self):
        """Тест успешного входа"""
        data = {
            'username': 'testuser1',
            'password': 'testpass123',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)


class StatusViewsTest(BaseTestCase):
    """Тесты для представлений статусов"""
    
    def test_status_list_view_requires_auth(self):
        """Тест доступа к списку статусов без авторизации"""
        response = self.client.get(reverse('statuses_index'))
        self.assertEqual(response.status_code, 302)
    
    def test_status_list_view_with_auth(self):
        """Тест списка статусов с авторизацией"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('statuses_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.status1.name)
    
    def test_status_create_view(self):
        """Тест создания статуса"""
        self.client.force_login(self.user1)
        
        data = {'name': 'New Status'}
        response = self.client.post(reverse('status_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Status.objects.filter(name='New Status').exists())


class LabelViewsTest(BaseTestCase):
    """Тесты для представлений меток"""
    
    def test_label_list_view_requires_auth(self):
        """Тест доступа к списку меток без авторизации"""
        response = self.client.get(reverse('labels_index'))
        self.assertEqual(response.status_code, 302)
    
    def test_label_list_view_with_auth(self):
        """Тест списка меток с авторизацией"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('labels_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.label1.name)
    
    def test_label_create_view(self):
        """Тест создания метки"""
        self.client.force_login(self.user1)
        
        data = {'name': 'New Label'}
        response = self.client.post(reverse('label_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Label.objects.filter(name='New Label').exists())


class TaskViewsTest(BaseTestCase):
    """Тесты для представлений задач"""
    
    def test_task_list_view_requires_auth(self):
        """Тест доступа к списку задач без авторизации"""
        response = self.client.get(reverse('tasks_index'))
        self.assertEqual(response.status_code, 302)
    
    def test_task_list_view_with_auth(self):
        """Тест списка задач с авторизацией"""
        Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        
        self.client.force_login(self.user1)
        response = self.client.get(reverse('tasks_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
    
    def test_task_create_view(self):
        """Тест создания задачи"""
        self.client.force_login(self.user1)
        
        data = {
            'name': 'New Task',
            'description': 'Task description',
            'status': self.status1.pk,
            'executor': self.user2.pk,
        }
        response = self.client.post(reverse('task_create'), data)
        self.assertEqual(response.status_code, 302)
        
        task = Task.objects.get(name='New Task')
        self.assertEqual(task.author, self.user1)
        self.assertEqual(task.executor, self.user2)
    
    def test_task_detail_view(self):
        """Тест детального просмотра задачи"""
        task = Task.objects.create(
            name='Test Task',
            description='Test description',
            status=self.status1,
            author=self.user1,
            executor=self.user2
        )
        task.labels.add(self.label1)
        
        self.client.force_login(self.user1)
        response = self.client.get(reverse('task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')


class TaskFilterTest(BaseTestCase):
    """Тесты фильтрации задач"""
    
    def setUp(self):
        super().setUp()
        
        self.task1 = Task.objects.create(
            name='Task 1',
            status=self.status1,
            author=self.user1,
            executor=self.user2
        )
        self.task1.labels.add(self.label1)
        
        self.task2 = Task.objects.create(
            name='Task 2',
            status=self.status2,
            author=self.user2,
            executor=self.user1
        )
        self.task2.labels.add(self.label2)
        
        self.task3 = Task.objects.create(
            name='Task 3',
            status=self.status1,
            author=self.user1
        )
    
    def test_filter_by_status(self):
        """Тест фильтрации по статусу"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {
            'status': self.status1.pk
        })
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 3')
        self.assertNotContains(response, 'Task 2')
    
    def test_filter_by_executor(self):
        """Тест фильтрации по исполнителю"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {
            'executor': self.user1.pk
        })
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Task 2')
        self.assertNotContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 3')
    
    def test_filter_by_label(self):
        """Тест фильтрации по метке"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {
            'label': self.label1.pk
    })
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')
        self.assertNotContains(response, 'Task 3')
    
    def test_filter_self_tasks(self):
        """Тест фильтрации собственных задач"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {
            'self_tasks': 'on'
        })
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 3')
        self.assertNotContains(response, 'Task 2')
    
    def test_combined_filters(self):
        """Тест комбинированных фильтров"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {
            'status': self.status1.pk,
            'self_tasks': 'on'
        })
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 3')
        self.assertNotContains(response, 'Task 2')


class ModelTest(BaseTestCase):
    """Тесты моделей"""
    
    def test_status_str(self):
        """Тест строкового представления статуса"""
        self.assertEqual(str(self.status1), 'New')
    
    def test_label_str(self):
        """Тест строкового представления метки"""
        self.assertEqual(str(self.label1), 'Bug')
    
    def test_task_str(self):
        """Тест строкового представления задачи"""
        task = Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        self.assertEqual(str(task), 'Test Task')
    
    def test_task_with_labels(self):
        """Тест задачи с метками"""
        task = Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        task.labels.add(self.label1, self.label2)
        
        self.assertEqual(task.labels.count(), 2)
        self.assertIn(self.label1, task.labels.all())
        self.assertIn(self.label2, task.labels.all())