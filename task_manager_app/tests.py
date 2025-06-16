from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from .models import Status, Task


class UserTestCase(TestCase):
    """Тесты для пользователей"""
    
    def setUp(self):
        """Настройка тестов"""
        self.client = Client()
        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        self.user = User.objects.create_user(
            username='existinguser',
            password='testpass123',
            first_name='Existing',
            last_name='User'
        )

    def test_users_list_view(self):
        """Тест списка пользователей"""
        response = self.client.get(reverse('users_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'existinguser')

    def test_user_create_get(self):
        """Тест GET запроса на страницу регистрации"""
        response = self.client.get(reverse('user_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign up')

    def test_user_create_post_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(reverse('user_create'), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Проверяем, что пользователь создан
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully registered' in str(m) for m in messages))

    def test_user_create_post_invalid(self):
        """Тест регистрации с некорректными данными"""
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'different_password'
        
        response = self.client.post(reverse('user_create'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_user_update_get_own_profile(self):
        """Тест GET запроса на редактирование собственного профиля"""
        self.client.login(username='existinguser', password='testpass123')
        response = self.client.get(reverse('user_update', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit user')

    def test_user_update_post_success(self):
        """Тест успешного обновления пользователя"""
        self.client.login(username='existinguser', password='testpass123')
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'username': 'existinguser'
        }
        
        response = self.client.post(reverse('user_update', args=[self.user.pk]), update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users_index'))
        
        # Проверяем, что данные обновились
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully updated' in str(m) for m in messages))

    def test_user_update_other_user_denied(self):
        """Тест запрета на редактирование чужого профиля"""
        other_user = User.objects.create_user(username='otheruser', password='test123')
        self.client.login(username='existinguser', password='testpass123')
        
        response = self.client.get(reverse('user_update', args=[other_user.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users_index'))

    def test_user_delete_get_own_profile(self):
        """Тест GET запроса на удаление собственного профиля"""
        self.client.login(username='existinguser', password='testpass123')
        response = self.client.get(reverse('user_delete', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete user')

    def test_user_delete_post_success(self):
        """Тест успешного удаления пользователя"""
        self.client.login(username='existinguser', password='testpass123')
        
        response = self.client.post(reverse('user_delete', args=[self.user.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users_index'))
        
        # Проверяем, что пользователь удален
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully deleted' in str(m) for m in messages))

    def test_user_delete_other_user_denied(self):
        """Тест запрета на удаление чужого профиля"""
        other_user = User.objects.create_user(username='otheruser', password='test123')
        self.client.login(username='existinguser', password='testpass123')
        
        response = self.client.get(reverse('user_delete', args=[other_user.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users_index'))

    def test_login_get(self):
        """Тест GET запроса на страницу входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_post_success(self):
        """Тест успешного входа"""
        login_data = {
            'username': 'existinguser',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_login_post_invalid(self):
        """Тест входа с неправильными данными"""
        login_data = {
            'username': 'existinguser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 200)
        # Проверяем, что пользователь остался на странице логина
        self.assertContains(response, 'Login')

    def test_logout(self):
        """Тест выхода"""
        self.client.login(username='existinguser', password='testpass123')
        
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_access_control_update_without_login(self):
        """Тест доступа к редактированию без авторизации"""
        response = self.client.get(reverse('user_update', args=[self.user.pk]))
        self.assertEqual(response.status_code, 302)
        # Неавторизованные пользователи редиректятся на /users/ (не могут редактировать чужой профиль)
        self.assertEqual(response.url, '/users/')

    def test_access_control_delete_without_login(self):
        """Тест доступа к удалению без авторизации"""
        response = self.client.get(reverse('user_delete', args=[self.user.pk]))
        self.assertEqual(response.status_code, 302)
        # Неавторизованные пользователи редиректятся на /users/ (не могут удалять чужой профиль)
        self.assertEqual(response.url, '/users/')

    def test_user_delete_with_tasks(self):
        """Тест запрета удаления пользователя со связанными задачами"""
        # Создаем статус и задачу
        status = Status.objects.create(name='Test Status')
        Task.objects.create(
            name='Test Task',
            status=status,
            author=self.user
        )
        
        self.client.login(username='existinguser', password='testpass123')
        response = self.client.post(reverse('user_delete', args=[self.user.pk]))
        
        # Пользователь не должен быть удален
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        
        # Должно быть сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Cannot delete user that is in use' in str(m) for m in messages))


class StatusTestCase(TestCase):
    """Тесты для статусов"""
    
    def setUp(self):
        """Настройка тестов"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.status_data = {
            'name': 'Test Status'
        }
        self.status = Status.objects.create(name='Existing Status')

    def test_status_list_view_requires_login(self):
        """Тест что список статусов требует авторизации"""
        response = self.client.get(reverse('statuses_index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_status_list_view_authenticated(self):
        """Тест списка статусов для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('statuses_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Existing Status')

    def test_status_create_get_requires_login(self):
        """Тест что страница создания статуса требует авторизации"""
        response = self.client.get(reverse('status_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_status_create_get_authenticated(self):
        """Тест GET запроса на страницу создания статуса"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('status_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create status')

    def test_status_create_post_success(self):
        """Тест успешного создания статуса"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('status_create'), self.status_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('statuses_index'))
        
        # Проверяем, что статус создан
        self.assertTrue(Status.objects.filter(name='Test Status').exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully created' in str(m) for m in messages))

    def test_status_create_post_invalid(self):
        """Тест создания статуса с некорректными данными"""
        self.client.login(username='testuser', password='testpass123')
        invalid_data = {'name': ''}
        
        response = self.client.post(reverse('status_create'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Status.objects.filter(name='').exists())

    def test_status_update_get_requires_login(self):
        """Тест что страница редактирования статуса требует авторизации"""
        response = self.client.get(reverse('status_update', args=[self.status.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_status_update_get_authenticated(self):
        """Тест GET запроса на страницу редактирования статуса"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('status_update', args=[self.status.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit status')

    def test_status_update_post_success(self):
        """Тест успешного обновления статуса"""
        self.client.login(username='testuser', password='testpass123')
        update_data = {'name': 'Updated Status'}
        
        response = self.client.post(reverse('status_update', args=[self.status.pk]), update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('statuses_index'))
        
        # Проверяем, что данные обновились
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Updated Status')
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully updated' in str(m) for m in messages))

    def test_status_delete_get_requires_login(self):
        """Тест что страница удаления статуса требует авторизации"""
        response = self.client.get(reverse('status_delete', args=[self.status.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_status_delete_get_authenticated(self):
        """Тест GET запроса на страницу удаления статуса"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('status_delete', args=[self.status.pk]))
        from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from .models import Status


class UserTestCase(TestCase):
    """Тесты для пользователей"""
    
    def setUp(self):
        """Настройка тестов"""
        self.client = Client()
        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        self.user = User.objects.create_user(
            username='existinguser',
            password='testpass123',
            first_name='Existing',
            last_name='User'
        )

    def test_users_list_view(self):
        """Тест списка пользователей"""
        response = self.client.get(reverse('users_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'existinguser')

    def test_user_create_get(self):
        """Тест GET запроса на страницу регистрации"""
        response = self.client.get(reverse('user_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign up')

    def test_user_create_post_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(reverse('user_create'), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Проверяем, что пользователь создан
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully registered' in str(m) for m in messages))

    def test_user_create_post_invalid(self):
        """Тест регистрации с некорректными данными"""
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'different_password'
        
        response = self.client.post(reverse('user_create'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_user_update_get_own_profile(self):
        """Тест GET запроса на редактирование собственного профиля"""
        self.client.login(username='existinguser', password='testpass123')
        response = self.client.get(reverse('user_update', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit user')

    def test_user_update_post_success(self):
        """Тест успешного обновления пользователя"""
        self.client.login(username='existinguser', password='testpass123')
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'username': 'existinguser'
        }
        
        response = self.client.post(reverse('user_update', args=[self.user.pk]), update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users_index'))
        
        # Проверяем, что данные обновились
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully updated' in str(m) for m in messages))

    def test_user_update_other_user_denied(self):
        """Тест запрета на редактирование чужого профиля"""
        other_user = User.objects.create_user(username='otheruser', password='test123')
        self.client.login(username='existinguser', password='testpass123')
        
        response = self.client.get(reverse('user_update', args=[other_user.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users_index'))

    def test_user_delete_get_own_profile(self):
        """Тест GET запроса на удаление собственного профиля"""
        self.client.login(username='existinguser', password='testpass123')
        response = self.client.get(reverse('user_delete', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete user')

    def test_user_delete_post_success(self):
        """Тест успешного удаления пользователя"""
        self.client.login(username='existinguser', password='testpass123')
        
        response = self.client.post(reverse('user_delete', args=[self.user.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users_index'))
        
        # Проверяем, что пользователь удален
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully deleted' in str(m) for m in messages))

    def test_user_delete_other_user_denied(self):
        """Тест запрета на удаление чужого профиля"""
        other_user = User.objects.create_user(username='otheruser', password='test123')
        self.client.login(username='existinguser', password='testpass123')
        
        response = self.client.get(reverse('user_delete', args=[other_user.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users_index'))

    def test_login_get(self):
        """Тест GET запроса на страницу входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_post_success(self):
        """Тест успешного входа"""
        login_data = {
            'username': 'existinguser',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_login_post_invalid(self):
        """Тест входа с неправильными данными"""
        login_data = {
            'username': 'existinguser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 200)
        # Проверяем, что пользователь остался на странице логина
        self.assertContains(response, 'Login')

    def test_logout(self):
        """Тест выхода"""
        self.client.login(username='existinguser', password='testpass123')
        
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_access_control_update_without_login(self):
        """Тест доступа к редактированию без авторизации"""
        response = self.client.get(reverse('user_update', args=[self.user.pk]))
        self.assertEqual(response.status_code, 302)
        # Неавторизованные пользователи редиректятся на /users/ (не могут редактировать чужой профиль)
        self.assertEqual(response.url, '/users/')

    def test_access_control_delete_without_login(self):
        """Тест доступа к удалению без авторизации"""
        response = self.client.get(reverse('user_delete', args=[self.user.pk]))
        self.assertEqual(response.status_code, 302)
        # Неавторизованные пользователи редиректятся на /users/ (не могут удалять чужой профиль)
        self.assertEqual(response.url, '/users/')


class StatusTestCase(TestCase):
    """Тесты для статусов"""
    
    def setUp(self):
        """Настройка тестов"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.status_data = {
            'name': 'Test Status'
        }
        self.status = Status.objects.create(name='Existing Status')

    def test_status_list_view_requires_login(self):
        """Тест что список статусов требует авторизации"""
        response = self.client.get(reverse('statuses_index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_status_list_view_authenticated(self):
        """Тест списка статусов для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('statuses_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Existing Status')

    def test_status_create_get_requires_login(self):
        """Тест что страница создания статуса требует авторизации"""
        response = self.client.get(reverse('status_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_status_create_get_authenticated(self):
        """Тест GET запроса на страницу создания статуса"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('status_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create status')

    def test_status_create_post_success(self):
        """Тест успешного создания статуса"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('status_create'), self.status_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('statuses_index'))
        
        # Проверяем, что статус создан
        self.assertTrue(Status.objects.filter(name='Test Status').exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully created' in str(m) for m in messages))

    def test_status_create_post_invalid(self):
        """Тест создания статуса с некорректными данными"""
        self.client.login(username='testuser', password='testpass123')
        invalid_data = {'name': ''}
        
        response = self.client.post(reverse('status_create'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Status.objects.filter(name='').exists())

    def test_status_update_get_requires_login(self):
        """Тест что страница редактирования статуса требует авторизации"""
        response = self.client.get(reverse('status_update', args=[self.status.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_status_update_get_authenticated(self):
        """Тест GET запроса на страницу редактирования статуса"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('status_update', args=[self.status.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit status')

    def test_status_update_post_success(self):
        """Тест успешного обновления статуса"""
        self.client.login(username='testuser', password='testpass123')
        update_data = {'name': 'Updated Status'}
        
        response = self.client.post(reverse('status_update', args=[self.status.pk]), update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('statuses_index'))
        
        # Проверяем, что данные обновились
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Updated Status')
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully updated' in str(m) for m in messages))

    def test_status_delete_get_requires_login(self):
        """Тест что страница удаления статуса требует авторизации"""
        response = self.client.get(reverse('status_delete', args=[self.status.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_status_delete_get_authenticated(self):
        """Тест GET запроса на страницу удаления статуса"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('status_delete', args=[self.status.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete status')

    def test_status_delete_post_success(self):
        """Тест успешного удаления статуса"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('status_delete', args=[self.status.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('statuses_index'))
        
        # Проверяем, что статус удален
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully deleted' in str(m) for m in messages))

    def test_status_name_uniqueness(self):
        """Тест уникальности имени статуса"""
        self.client.login(username='testuser', password='testpass123')
        duplicate_data = {'name': 'Existing Status'}
        
        response = self.client.post(reverse('status_create'), duplicate_data)
        self.assertEqual(response.status_code, 200)
        # Проверяем, что второй статус с таким же именем не создался
        self.assertEqual(Status.objects.filter(name='Existing Status').count(), 1)

    def test_status_delete_with_tasks(self):
        """Тест запрета удаления статуса со связанными задачами"""
        # Создаем пользователя и задачу
        author = User.objects.create_user(username='author', password='test123')
        Task.objects.create(
            name='Test Task',
            status=self.status,
            author=author
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('status_delete', args=[self.status.pk]))
        
        # Статус не должен быть удален
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())
        
        # Должно быть сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Cannot delete status that is in use' in str(m) for m in messages))


class TaskTestCase(TestCase):
    """Тесты для задач"""
    
    def setUp(self):
        """Настройка тестов"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.status = Status.objects.create(name='Test Status')
        self.task_data = {
            'name': 'Test Task',
            'description': 'Test Description',
            'status': self.status.pk,
            'executor': self.other_user.pk
        }
        self.task = Task.objects.create(
            name='Existing Task',
            status=self.status,
            author=self.user
        )

    def test_task_list_view_requires_login(self):
        """Тест что список задач требует авторизации"""
        response = self.client.get(reverse('tasks_index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_task_list_view_authenticated(self):
        """Тест списка задач для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('tasks_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Existing Task')

    def test_task_detail_view_requires_login(self):
        """Тест что просмотр задачи требует авторизации"""
        response = self.client.get(reverse('task_detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_task_detail_view_authenticated(self):
        """Тест просмотра задачи для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task_detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Existing Task')

    def test_task_create_get_requires_login(self):
        """Тест что страница создания задачи требует авторизации"""
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_task_create_get_authenticated(self):
        """Тест GET запроса на страницу создания задачи"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create task')

    def test_task_create_post_success(self):
        """Тест успешного создания задачи"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('task_create'), self.task_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks_index'))
        
        # Проверяем, что задача создана
        task = Task.objects.get(name='Test Task')
        self.assertEqual(task.author, self.user)
        self.assertEqual(task.status, self.status)
        self.assertEqual(task.executor, self.other_user)
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully created' in str(m) for m in messages))

    def test_task_create_post_invalid(self):
        """Тест создания задачи с некорректными данными"""
        self.client.login(username='testuser', password='testpass123')
        invalid_data = {'name': '', 'status': ''}
        
        response = self.client.post(reverse('task_create'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(name='').exists())

    def test_task_update_get_requires_login(self):
        """Тест что страница редактирования задачи требует авторизации"""
        response = self.client.get(reverse('task_update', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_task_update_get_authenticated(self):
        """Тест GET запроса на страницу редактирования задачи"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task_update', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit task')

    def test_task_update_post_success(self):
        """Тест успешного обновления задачи"""
        self.client.login(username='testuser', password='testpass123')
        update_data = {
            'name': 'Updated Task',
            'description': 'Updated Description',
            'status': self.status.pk,
            'executor': self.other_user.pk
        }
        
        response = self.client.post(reverse('task_update', args=[self.task.pk]), update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks_index'))
        
        # Проверяем, что данные обновились
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Updated Task')
        self.assertEqual(self.task.description, 'Updated Description')
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully updated' in str(m) for m in messages))

    def test_task_delete_get_requires_login(self):
        """Тест что страница удаления задачи требует авторизации"""
        response = self.client.get(reverse('task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_task_delete_get_authenticated_author(self):
        """Тест GET запроса на страницу удаления задачи (автор)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete task')

    def test_task_delete_get_not_author(self):
        """Тест запрета доступа к удалению задачи для не-автора"""
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks_index'))
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Only task author can delete it' in str(m) for m in messages))

    def test_task_delete_post_success(self):
        """Тест успешного удаления задачи"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks_index'))
        
        # Проверяем, что задача удалена
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully deleted' in str(m) for m in messages))

    def test_task_delete_post_not_author(self):
        """Тест запрета удаления задачи для не-автора"""
        self.client.login(username='otheruser', password='testpass123')
        
        response = self.client.post(reverse('task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks_index'))
        
        # Задача не должна быть удалена
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Only task author can delete it' in str(m) for m in messages))

    def test_task_author_set_automatically(self):
        """Тест автоматической установки автора задачи"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('task_create'), self.task_data)
        
        task = Task.objects.get(name='Test Task')
        self.assertEqual(task.author, self.user)

    def test_task_executor_optional(self):
        """Тест что исполнитель задачи опционален"""
        self.client.login(username='testuser', password='testpass123')
        data_without_executor = self.task_data.copy()
        data_without_executor['executor'] = ''
        
        response = self.client.post(reverse('task_create'), data_without_executor)
        self.assertEqual(response.status_code, 302)
        
        task = Task.objects.get(name='Test Task')
        self.assertIsNone(task.executor)

    def test_status_delete_post_success(self):
        """Тест успешного удаления статуса"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('status_delete', args=[self.status.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('statuses_index'))
        
        # Проверяем, что статус удален
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())
        
        # Проверяем сообщение об успехе
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully deleted' in str(m) for m in messages))

    def test_status_name_uniqueness(self):
        """Тест уникальности имени статуса"""
        self.client.login(username='testuser', password='testpass123')
        duplicate_data = {'name': 'Existing Status'}
        
        response = self.client.post(reverse('status_create'), duplicate_data)
        self.assertEqual(response.status_code, 200)
        # Проверяем, что второй статус с таким же именем не создался
        self.assertEqual(Status.objects.filter(name='Existing Status').count(), 1)