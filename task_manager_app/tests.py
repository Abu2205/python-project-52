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