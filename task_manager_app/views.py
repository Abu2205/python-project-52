from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.db.models import ProtectedError

from .forms import UserRegistrationForm, UserUpdateForm, StatusForm
from .models import Status


class IndexView(TemplateView):
    """Главная страница с приветствием"""
    template_name = 'index.html'


# ========== USER VIEWS ==========

class UserListView(ListView):
    """Список всех пользователей"""
    model = User
    template_name = 'users/index.html'
    context_object_name = 'users'


class UserCreateView(SuccessMessageMixin, CreateView):
    """Регистрация нового пользователя"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/create.html'
    success_url = reverse_lazy('login')
    success_message = _('User successfully registered')


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование пользователя"""
    model = User
    form_class = UserUpdateForm
    template_name = 'users/update.html'
    success_url = reverse_lazy('users_index')
    success_message = _('User successfully updated')

    def dispatch(self, request, *args, **kwargs):
        """Проверяем, что пользователь может редактировать только себя"""
        if request.user.id != kwargs.get('pk'):
            messages.error(request, _('You have no rights to change another user.'))
            return redirect('users_index')
        return super().dispatch(request, *args, **kwargs)


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление пользователя"""
    model = User
    template_name = 'users/delete.html'
    success_url = reverse_lazy('users_index')
    success_message = _('User successfully deleted')

    def dispatch(self, request, *args, **kwargs):
        """Проверяем, что пользователь может удалять только себя"""
        if request.user.id != kwargs.get('pk'):
            messages.error(request, _('You have no rights to change another user.'))
            return redirect('users_index')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Проверяем, что у пользователя нет связанных задач перед удалением"""
        user = self.get_object()
        # TODO: Добавить проверку на связанные задачи когда будет модель Task
        messages.success(request, self.success_message)
        return super().post(request, *args, **kwargs)


class UserLoginView(SuccessMessageMixin, LoginView):
    """Вход пользователя"""
    template_name = 'users/login.html'
    success_message = _('You are logged in')
    
    def get_success_url(self):
        return reverse_lazy('index')


class UserLogoutView(LogoutView):
    """Выход пользователя"""
    next_page = '/'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, _('You are logged out'))
        return super().dispatch(request, *args, **kwargs)


# ========== STATUS VIEWS ==========

class StatusListView(LoginRequiredMixin, ListView):
    """Список всех статусов"""
    model = Status
    template_name = 'statuses/index.html'
    context_object_name = 'statuses'


class StatusCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание нового статуса"""
    model = Status
    form_class = StatusForm
    template_name = 'statuses/create.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Status successfully created')


class StatusUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование статуса"""
    model = Status
    form_class = StatusForm
    template_name = 'statuses/update.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Status successfully updated')


class StatusDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление статуса"""
    model = Status
    template_name = 'statuses/delete.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Status successfully deleted')

    def post(self, request, *args, **kwargs):
        """Проверяем, что статус не связан с задачами перед удалением"""
        status = self.get_object()
        try:
            # TODO: Добавить проверку на связанные задачи когда будет модель Task
            # if status.tasks.exists():
            #     messages.error(request, _('Cannot delete status that is in use'))
            #     return redirect('statuses_index')
            
            messages.success(request, self.success_message)
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _('Cannot delete status that is in use'))
            return redirect('statuses_index')