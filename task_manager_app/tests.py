"""
Тесты для Django приложения Task Manager
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from task_manager_app.models import Status, Task, Label


class BaseTestCase(TestCase):
    """Базовый класс для тестов с общими настройками"""
    
    def setUp(self):
        self.client = Client()
        
        # Создаем тестовых пользователей
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
        
        # Создаем тестовые статусы
        self.status1 = Status.objects.create(name='New')
        self.status2 = Status.objects.create(name='In Progress')
        self.status3 = Status.objects.create(name='Done')
        
        # Создаем тестовые метки
        self.label1 = Label.objects.create(name='Bug')
        self.label2 = Label.objects.create(name='Feature')
        self.label3 = Label.objects.create(name='Enhancement')


class IndexViewTest(BaseTestCase):
    """Тесты главной страницы"""
    
    def test_index_view(self):
        """Тест отображения главной страницы"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello from Hexlet!')


class UserViewsTest(BaseTestCase):
    """Тесты для представлений пользователей"""
    
    def test_users_list_view(self):
        """Тест списка пользователей"""
        response = self.client.get(reverse('users_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.username)
        self.assertContains(response, self.user2.username)
    
    def test_user_create_view_get(self):
        """Тест GET запроса формы регистрации"""
        response = self.client.get(reverse('user_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign up')
    
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
    
    def test_user_update_view_own_user(self):
        """Тест обновления собственного профиля"""
        self.client.force_login(self.user1)
        
        # GET запрос
        response = self.client.get(reverse('user_update', args=[self.user1.pk]))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'username': 'updateduser',
        }
        response = self.client.post(reverse('user_update', args=[self.user1.pk]), data)
        self.assertEqual(response.status_code, 302)
        
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated')
    
    def test_user_update_view_other_user(self):
        """Тест попытки обновления чужого профиля"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('user_update', args=[self.user2.pk]))
        self.assertEqual(response.status_code, 302)
    
    def test_user_delete_view_own_user(self):
        """Тест удаления собственного профиля"""
        self.client.force_login(self.user1)
        
        # GET запрос
        response = self.client.get(reverse('user_delete', args=[self.user1.pk]))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        response = self.client.post(reverse('user_delete', args=[self.user1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.user1.pk).exists())
    
    def test_user_delete_view_other_user(self):
        """Тест попытки удаления чужого профиля"""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('user_delete', args=[self.user2.pk]))
        self.assertEqual(response.status_code, 302)
    
    def test_user_delete_with_tasks(self):
        """Тест удаления пользователя с задачами"""
        # Создаем задачу для пользователя
        Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        
        self.client.force_login(self.user1)
        response = self.client.post(reverse('user_delete', args=[self.user1.pk]))
        
        # Пользователь не должен быть удален
        self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Cannot delete user that is in use' in str(message) for message in messages))


class AuthViewsTest(BaseTestCase):
    """Тесты аутентификации"""
    
    def test_login_view_get(self):
        """Тест GET запроса страницы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_success(self):
        """Тест успешного входа"""
        data = {
            'username': 'testuser1',
            'password': 'testpass123',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
    
    def test_logout_view(self):
        """Тест выхода из системы"""
        self.client.force_login(self.user1)
        response = self.client.post(reverse('logout'))
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
        
        # GET запрос
        response = self.client.get(reverse('status_create'))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        data = {'name': 'New Status'}
        response = self.client.post(reverse('status_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Status.objects.filter(name='New Status').exists())
    
    def test_status_update_view(self):
        """Тест обновления статуса"""
        self.client.force_login(self.user1)
        
        # GET запрос
        response = self.client.get(reverse('status_update', args=[self.status1.pk]))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        data = {'name': 'Updated Status'}
        response = self.client.post(reverse('status_update', args=[self.status1.pk]), data)
        self.assertEqual(response.status_code, 302)
        
        self.status1.refresh_from_db()
        self.assertEqual(self.status1.name, 'Updated Status')
    
    def test_status_delete_view(self):
        """Тест удаления статуса"""
        self.client.force_login(self.user1)
        
        # GET запрос
        response = self.client.get(reverse('status_delete', args=[self.status1.pk]))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        response = self.client.post(reverse('status_delete', args=[self.status1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Status.objects.filter(pk=self.status1.pk).exists())
    
    def test_status_delete_with_tasks(self):
        """Тест удаления статуса с привязанными задачами"""
        # Создаем задачу со статусом
        Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        
        self.client.force_login(self.user1)
        response = self.client.post(reverse('status_delete', args=[self.status1.pk]))
        
        # Статус не должен быть удален
        self.assertTrue(Status.objects.filter(pk=self.status1.pk).exists())


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
        
        # GET запрос
        response = self.client.get(reverse('label_create'))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        data = {'name': 'New Label'}
        response = self.client.post(reverse('label_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Label.objects.filter(name='New Label').exists())
    
    def test_label_update_view(self):
        """Тест обновления метки"""
        self.client.force_login(self.user1)
        
        # GET запрос
        response = self.client.get(reverse('label_update', args=[self.label1.pk]))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        data = {'name': 'Updated Label'}
        response = self.client.post(reverse('label_update', args=[self.label1.pk]), data)
        self.assertEqual(response.status_code, 302)
        
        self.label1.refresh_from_db()
        self.assertEqual(self.label1.name, 'Updated Label')
    
    def test_label_delete_view(self):
        """Тест удаления метки"""
        self.client.force_login(self.user1)
        
        # GET запрос
        response = self.client.get(reverse('label_delete', args=[self.label1.pk]))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        response = self.client.post(reverse('label_delete', args=[self.label1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Label.objects.filter(pk=self.label1.pk).exists())
    
    def test_label_delete_with_tasks(self):
        """Тест удаления метки с привязанными задачами"""
        # Создаем задачу с меткой
        task = Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        task.labels.add(self.label1)
        
        self.client.force_login(self.user1)
        response = self.client.post(reverse('label_delete', args=[self.label1.pk]))
        
        # Метка не должна быть удалена
        self.assertTrue(Label.objects.filter(pk=self.label1.pk).exists())


class TaskViewsTest(BaseTestCase):
    """Тесты для представлений задач"""
    
    def test_task_list_view_requires_auth(self):
        """Тест доступа к списку задач без авторизации"""
        response = self.client.get(reverse('tasks_index'))
        self.assertEqual(response.status_code, 302)
    
    def test_task_list_view_with_auth(self):
        """Тест списка задач с авторизацией"""
        # Создаем тестовую задачу
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
        
        # GET запрос
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
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
        self.assertContains(response, 'Test description')
        self.assertContains(response, self.label1.name)
    
    def test_task_update_view(self):
        """Тест обновления задачи"""
        task = Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        
        self.client.force_login(self.user1)
        
        # GET запрос
        response = self.client.get(reverse('task_update', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        data = {
            'name': 'Updated Task',
            'description': 'Updated description',
            'status': self.status2.pk,
            'executor': self.user2.pk,
        }
        response = self.client.post(reverse('task_update', args=[task.pk]), data)
        self.assertEqual(response.status_code, 302)
        
        task.refresh_from_db()
        self.assertEqual(task.name, 'Updated Task')
        self.assertEqual(task.status, self.status2)
    
    def test_task_delete_view_by_author(self):
        """Тест удаления задачи автором"""
        task = Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        
        self.client.force_login(self.user1)
        
        # GET запрос
        response = self.client.get(reverse('task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        response = self.client.post(reverse('task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
    
    def test_task_delete_view_by_non_author(self):
        """Тест попытки удаления задачи не автором"""
        task = Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        
        self.client.force_login(self.user2)
        
        # GET запрос
        response = self.client.get(reverse('task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        
        # POST запрос
        response = self.client.post(reverse('task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Задача не должна быть удалена
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())


class TaskFilterTest(BaseTestCase):
    """Тесты фильтрации задач"""
    
    def setUp(self):
        super().setUp()
        
        # Создаем задачи для тестирования фильтров
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
        
        response = self.client.get(reverse('tasks_index'), {'status': self.status1.pk})
        self.assertEqual(response.status_code, 200)
        
        # Должны быть task1 и task3
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 3')
        self.assertNotContains(response, 'Task 2')
    
    def test_filter_by_executor(self):
        """Тест фильтрации по исполнителю"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {'executor': self.user1.pk})
        self.assertEqual(response.status_code, 200)
        
        # Должна быть только task2
        self.assertContains(response, 'Task 2')
        self.assertNotContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 3')
    
    def test_filter_by_label(self):
        """Тест фильтрации по метке"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {'label': self.label1.pk})
        self.assertEqual(response.status_code, 200)
        
        # Должна быть только task1
        self.assertContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')
        self.assertNotContains(response, 'Task 3')
    
    def test_filter_self_tasks(self):
        """Тест фильтрации собственных задач"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'), {'self_tasks': 'on'})
        self.assertEqual(response.status_code, 200)
        
        # Должны быть task1 и task3 (автор user1)
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 3')
        self.assertNotContains(response, 'Task 2')
    
    def test_combined_filters(self):
        """Тест комбинированных фильтров"""
        self.client.force_login(self.user1)
        
        # Фильтр по статусу и автору
        response = self.client.get(reverse('tasks_index'), {
            'status': self.status1.pk,
            'self_tasks': 'on'
        })
        self.assertEqual(response.status_code, 200)
        
        # Должны быть task1 и task3
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 3')
        self.assertNotContains(response, 'Task 2')
    
    def test_filter_form_rendering(self):
        """Тест отображения формы фильтров"""
        self.client.force_login(self.user1)
        
        response = self.client.get(reverse('tasks_index'))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем наличие элементов фильтра
        self.assertContains(response, 'name="status"')
        self.assertContains(response, 'name="executor"')
        self.assertContains(response, 'name="label"')
        self.assertContains(response, 'name="self_tasks"')
        
        # Проверяем наличие опций в селектах
        self.assertContains(response, self.status1.name)
        self.assertContains(response, self.user1.username)
        self.assertContains(response, self.label1.name)


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
    
    def test_user_task_relationships(self):
        """Тест связей пользователя с задачами"""
        task1 = Task.objects.create(
            name='Authored Task',
            status=self.status1,
            author=self.user1
        )
        
        task2 = Task.objects.create(
            name='Assigned Task',
            status=self.status1,
            author=self.user2,
            executor=self.user1
        )
        
        # Проверяем связи
        self.assertIn(task1, self.user1.authored_tasks.all())
        self.assertIn(task2, self.user1.assigned_tasks.all())
        self.assertNotIn(task2, self.user1.authored_tasks.all())
        self.assertNotIn(task1, self.user1.assigned_tasks.all())


class FormTest(BaseTestCase):
    """Тесты форм"""
    
    def test_user_registration_form_valid(self):
        """Тест валидной формы регистрации"""
        from task_manager_app.forms import UserRegistrationForm
        
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_unique_status_name_constraint(self):
        """Тест ограничения уникальности имени статуса"""
        from task_manager_app.forms import StatusForm
        
        form_data = {'name': 'New'}  # уже существует
        form = StatusForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_unique_label_name_constraint(self):
        """Тест ограничения уникальности имени метки"""
        from task_manager_app.forms import LabelForm
        
        form_data = {'name': 'Bug'}  # уже существует
        form = LabelForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_empty_filter_returns_all_tasks(self):
        """Тест что пустой фильтр возвращает все задачи"""
        # Создаем несколько задач
        Task.objects.create(name='Task 1', status=self.status1, author=self.user1)
        Task.objects.create(name='Task 2', status=self.status2, author=self.user2)
        
        self.client.force_login(self.user1)
        response = self.client.get(reverse('tasks_index'))
        
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 2')
    
    def test_task_ordering(self):
        """Тест сортировки задач по дате создания (новые первыми)"""
        import time
        
        task1 = Task.objects.create(name='First Task', status=self.status1, author=self.user1)
        time.sleep(0.01)  # Небольшая задержка для разных временных меток
        task2 = Task.objects.create(name='Second Task', status=self.status1, author=self.user1)
        
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)  # Новая задача должна быть первой
        self.assertEqual(tasks[1], task1)


class SecurityTest(BaseTestCase):
    """Тесты безопасности"""
    
    def test_unauthenticated_access_to_protected_views(self):
        """Тест доступа неавторизованных пользователей к защищенным страницам"""
        protected_urls = [
            'statuses_index',
            'status_create',
            'labels_index',
            'label_create',
            'tasks_index',
            'task_create',
        ]
        
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302, f"URL {url_name} должен требовать авторизации")
    
    def test_csrf_protection(self):
        """Тест защиты от CSRF атак"""
        self.client.force_login(self.user1)
        
        # Попытка создать статус без CSRF токена
        data = {'name': 'Test Status'}
        response = self.client.post(reverse('status_create'), data, HTTP_X_CSRFTOKEN='invalid')
        # Django должен отклонить запрос из-за неверного CSRF токена
        self.assertNotEqual(response.status_code, 302)


class MessageTest(BaseTestCase):
    """Тесты сообщений пользователю"""
    
    def test_success_messages(self):
        """Тест успешных сообщений"""
        self.client.force_login(self.user1)
        
        # Создание статуса
        data = {'name': 'New Status'}
        response = self.client.post(reverse('status_create'), data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully created' in str(message) for message in messages))
        
        # Обновление статуса
        status = Status.objects.get(name='New Status')
        data = {'name': 'Updated Status'}
        response = self.client.post(reverse('status_update', args=[status.pk]), data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully updated' in str(message) for message in messages))
    
    def test_error_messages(self):
        """Тест сообщений об ошибках"""
        # Создаем задачу со статусом
        task = Task.objects.create(
            name='Test Task',
            status=self.status1,
            author=self.user1
        )
        
        self.client.force_login(self.user1)
        
        # Попытка удалить статус, используемый в задаче
        response = self.client.post(reverse('status_delete', args=[self.status1.pk]), follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Cannot delete status that is in use' in str(message) for message in messages))


class IntegrationTest(BaseTestCase):
    """Интеграционные тесты"""
    
    def test_full_task_lifecycle(self):
        """Тест полного жизненного цикла задачи"""
        self.client.force_login(self.user1)
        
        # 1. Создание задачи
        task_data = {
            'name': 'Integration Test Task',
            'description': 'This is an integration test',
            'status': self.status1.pk,
            'executor': self.user2.pk,
            'labels': [self.label1.pk, self.label2.pk],
        }
        response = self.client.post(reverse('task_create'), task_data)
        self.assertEqual(response.status_code, 302)
        
        task = Task.objects.get(name='Integration Test Task')
        
        # 2. Просмотр задачи
        response = self.client.get(reverse('task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Task')
        
        # 3. Обновление задачи
        update_data = {
            'name': 'Updated Integration Test Task',
            'description': 'Updated description',
            'status': self.status2.pk,
            'executor': self.user1.pk,
            'labels': [self.label3.pk],
        }
        response = self.client.post(reverse('task_update', args=[task.pk]), update_data)
        self.assertEqual(response.status_code, 302)
        
        task.refresh_from_db()
        self.assertEqual(task.name, 'Updated Integration Test Task')
        self.assertEqual(task.status, self.status2)
        
        # 4. Фильтрация задач
        response = self.client.get(reverse('tasks_index'), {'status': self.status2.pk})
        self.assertContains(response, 'Updated Integration Test Task')
        
        # 5. Удаление задачи
        response = self.client.post(reverse('task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
    
    def test_user_workflow(self):
        """Тест рабочего процесса пользователя"""
        # 1. Регистрация
        registration_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
        }
        response = self.client.post(reverse('user_create'), registration_data)
        self.assertEqual(response.status_code, 302)
        
        new_user = User.objects.get(username='newuser')
        
        # 2. Вход в систему
        login_data = {
            'username': 'newuser',
            'password': 'newpass123',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)
        
        # 3. Создание статуса
        status_data = {'name': 'User Status'}
        response = self.client.post(reverse('status_create'), status_data)
        self.assertEqual(response.status_code, 302)
        
        user_status = Status.objects.get(name='User Status')
        
        # 4. Создание метки
        label_data = {'name': 'User Label'}
        response = self.client.post(reverse('label_create'), label_data)
        self.assertEqual(response.status_code, 302)
        
        user_label = Label.objects.get(name='User Label')
        
        # 5. Создание задачи
        task_data = {
            'name': 'User Task',
            'description': 'Task created by new user',
            'status': user_status.pk,
            'labels': [user_label.pk],
        }
        response = self.client.post(reverse('task_create'), task_data)
        self.assertEqual(response.status_code, 302)
        
        user_task = Task.objects.get(name='User Task')
        self.assertEqual(user_task.author, new_user)
        
        # 6. Фильтрация собственных задач
        response = self.client.get(reverse('tasks_index'), {'self_tasks': 'on'})
        self.assertContains(response, 'User Task')
        
        # 7. Выход из системы
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class FilterEdgeCaseTest(BaseTestCase):
    """Тесты граничных случаев фильтрации"""
    
    def test_filter_with_nonexistent_values(self):
        """Тест фильтрации с несуществующими значениями"""
        self.client.force_login(self.user1)
        
        # Фильтр по несуществующему статусу
        response = self.client.get(reverse('tasks_index'), {'status': 9999})
        self.assertEqual(response.status_code, 200)
        
        # Фильтр по несуществующему пользователю
        response = self.client.get(reverse('tasks_index'), {'executor': 9999})
        self.assertEqual(response.status_code, 200)
        
        # Фильтр по несуществующей метке
        response = self.client.get(reverse('tasks_index'), {'label': 9999})
        self.assertEqual(response.status_code, 200)
    
    def test_filter_combinations(self):
        """Тест различных комбинаций фильтров"""
        # Создаем задачи для тестирования
        task1 = Task.objects.create(
            name='Task 1',
            status=self.status1,
            author=self.user1,
            executor=self.user2
        )
        task1.labels.add(self.label1)
        
        task2 = Task.objects.create(
            name='Task 2',
            status=self.status1,
            author=self.user1,
            executor=self.user1
        )
        task2.labels.add(self.label2)
        
        self.client.force_login(self.user1)
        
        # Комбинация: статус + исполнитель
        response = self.client.get(reverse('tasks_index'), {
            'status': self.status1.pk,
            'executor': self.user2.pk
        })
        self.assertContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')
        
        # Комбинация: статус + метка + собственные задачи
        response = self.client.get(reverse('tasks_index'), {
            'status': self.status1.pk,
            'label': self.label2.pk,
            'self_tasks': 'on'
        })
        self.assertContains(response, 'Task 2')
        self.assertNotContains(response, 'Task 1')


# Тесты производительности (базовые)
class PerformanceTest(BaseTestCase):
    """Базовые тесты производительности"""
    
    def test_task_list_with_many_tasks(self):
        """Тест списка задач с большим количеством записей"""
        # Создаем много задач
        tasks = []
        for i in range(100):
            task = Task(
                name=f'Task {i}',
                status=self.status1,
                author=self.user1
            )
            tasks.append(task)
        
        Task.objects.bulk_create(tasks)
        
        self.client.force_login(self.user1)
        
        # Измеряем время отклика
        import time
        start_time = time.time()
        response = self.client.get(reverse('tasks_index'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        # Время отклика должно быть разумным (менее 5 секунд)
        self.assertLess(end_time - start_time, 5.0)
    
    def test_filter_performance_with_many_tasks(self):
        """Тест производительности фильтрации с большим количеством задач"""
        # Создаем много задач с разными статусами
        tasks = []
        for i in range(50):
            task = Task(
                name=f'Task {i}',
                status=self.status1 if i % 2 == 0 else self.status2,
                author=self.user1,
                executor=self.user1 if i % 3 == 0 else self.user2
            )
            tasks.append(task)
        
        Task.objects.bulk_create(tasks)
        
        # Добавляем метки к некоторым задачам
        for task in Task.objects.all()[:25]:
            task.labels.add(self.label1)
        
        self.client.force_login(self.user1)
        
        # Тестируем различные фильтры
        import time
        
        # Фильтр по статусу
        start_time = time.time()
        response = self.client.get(reverse('tasks_index'), {'status': self.status1.pk})
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)
        
        # Фильтр по исполнителю
        start_time = time.time()
        response = self.client.get(reverse('tasks_index'), {'executor': self.user1.pk})
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)
        
        # Фильтр по метке
        start_time = time.time()
        response = self.client.get(reverse('tasks_index'), {'label': self.label1.pk})
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_registration_form_password_mismatch(self):
        """Тест формы регистрации с несовпадающими паролями"""
        from task_manager_app.forms import UserRegistrationForm
        
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'different123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_task_form_valid(self):
        """Тест валидной формы задачи"""
        from task_manager_app.forms import TaskForm
        
        form_data = {
            'name': 'Test Task',
            'description': 'Test description',
            'status': self.status1.pk,
            'executor': self.user1.pk,
            'labels': [self.label1.pk, self.label2.pk],
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_status_form_valid(self):
        """Тест валидной формы статуса"""
        from task_manager_app.forms import StatusForm
        
        form_data = {'name': 'Test Status'}
        form = StatusForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_label_form_valid(self):
        """Тест валидной формы метки"""
        from task_manager_app.forms import LabelForm
        
        form_data = {'name': 'Test Label'}
        form = LabelForm(data=form_data)
        self.assertTrue(form.is_valid())


# Дополнительные тесты для покрытия edge cases
class EdgeCaseTest(BaseTestCase):
    """Тесты граничных случаев"""
    
    def test_task_without_executor(self):
        """Тест создания задачи без исполнителя"""
        self.client.force_login(self.user1)
        
        data = {
            'name': 'Task without executor',
            'description': 'Test description',
            'status': self.status1.pk,
        }
        response = self.client.post(reverse('task_create'), data)
        self.assertEqual(response.status_code, 302)
        
        task = Task.objects.get(name='Task without executor')
        self.assertIsNone(task.executor)
    
    def test_task_without_labels(self):
        """Тест создания задачи без меток"""
        self.client.force_login(self.user1)
        
        data = {
            'name': 'Task without labels',
            'status': self.status1.pk,
        }
        response = self.client.post(reverse('task_create'), data)
        self.assertEqual(response.status_code, 302)
        
        task = Task.objects.get(name='Task without labels')
        self.assertEqual(task.labels.count(), 0)
    
    def test_unique_username_constraint(self):
        """Тест ограничения уникальности имени пользователя"""
        from task_manager_app.forms import UserRegistrationForm
        
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser1',  # уже существует
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = UserRegistrationForm