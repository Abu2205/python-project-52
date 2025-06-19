from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.db.models import ProtectedError
from django_filters.views import FilterView
from .filters import TaskFilter
from .forms import UserRegistrationForm, UserUpdateForm, StatusForm, TaskForm, LabelForm, UserLoginForm
from .models import Status, Task, Label


class IndexView(TemplateView):
    """Главная страница с приветствием"""
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        

        if self.request.GET.get('test_rollbar'):
            a = None
            a.hello()
            
        return context


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
    success_message = _('Пользователь успешно зарегистрирован')


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование пользователя"""
    model = User
    form_class = UserUpdateForm
    template_name = 'users/update.html'
    success_url = reverse_lazy('users_index')
    success_message = _('Пользователь успешно изменен')

    def dispatch(self, request, *args, **kwargs):
        """Проверяем, что пользователь может редактировать только себя"""
        if request.user.id != kwargs.get('pk'):
            messages.error(request, _('У вас нет прав изменять другого пользователя.'))
            return redirect('users_index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Обрабатываем форму и перелогиниваем пользователя если пароль изменился"""
        user = form.save()
        password = form.cleaned_data.get('password1')
        if password:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        """Обрабатываем ошибки валидации - остаемся на той же странице"""
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Добавляем дополнительный контекст"""
        context = super().get_context_data(**kwargs)
        return context



class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление пользователя"""
    model = User
    template_name = 'users/delete.html'
    success_url = reverse_lazy('users_index')
    success_message = _('Пользователь успешно удален')

    def dispatch(self, request, *args, **kwargs):
        """Проверяем, что пользователь может удалять только себя"""
        if request.user.id != kwargs.get('pk'):
            messages.error(request, _('У вас нет прав изменять другого пользователя.'))
            return redirect('users_index')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Проверяем, что у пользователя нет связанных задач перед удалением"""
        user = self.get_object()
        try:
            if user.authored_tasks.exists() or user.assigned_tasks.exists():
                messages.error(request, _('Невозможно удалить пользователя, который используется'))
                return redirect('users_index')
            
            messages.success(request, self.success_message)
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _('Невозможно удалить пользователя, который используется'))
            return redirect('users_index')


class UserLoginView(SuccessMessageMixin, LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_message = _('Вы залогинены')
    
    def get_success_url(self):
        return reverse_lazy('index')


class UserLogoutView(LogoutView):
    """Выход пользователя"""
    next_page = '/'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, _('Вы разлогинены'))
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
    success_message = _('Статус успешно создан')


class StatusUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование статуса"""
    model = Status
    form_class = StatusForm
    template_name = 'statuses/update.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Статус успешно изменен')


class StatusDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление статуса"""
    model = Status
    template_name = 'statuses/delete.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Статус успешно удален')

    def post(self, request, *args, **kwargs):
        """Проверяем, что статус не связан с задачами перед удалением"""
        status = self.get_object()
        try:
            if status.task_set.exists():
                messages.error(request, _('Невозможно удалить статус, который используется'))
                return redirect('statuses_index')
            
            messages.success(request, self.success_message)
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _('Невозможно удалить статус, который используется'))
            return redirect('statuses_index')


# ========== TASK VIEWS ==========

class TaskListView(FilterView):
    """Список всех задач с фильтрацией"""
    model = Task
    template_name = 'tasks/index.html'
    context_object_name = 'tasks'
    filterset_class = TaskFilter
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """Просмотр задачи"""
    model = Task
    template_name = 'tasks/detail.html'
    context_object_name = 'task'


class TaskCreateView(SuccessMessageMixin, CreateView):
    """Создание новой задачи"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/create.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Задача успешно создана')

    def form_valid(self, form):
        """Устанавливаем автора задачи"""
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        else:
            from django.contrib.auth.models import User
            form.instance.author = User.objects.first()
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование задачи"""
    model = Task
    form_class = TaskForm
    template_name = 'tasks/update.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Задача успешно изменена')


class TaskDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление задачи"""
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Задача успешно удалена')

    def get(self, request, *args, **kwargs):
        """Проверяем права доступа при GET запросе"""
        task = self.get_object()
        if request.user != task.author:
            messages.error(request, _('Задачу может удалить только ее автор'))
            return redirect('tasks_index')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Проверяем права доступа при POST запросе"""
        task = self.get_object()
        if request.user != task.author:
            messages.error(request, _('Задачу может удалить только ее автор'))
            return redirect('tasks_index')
        return super().post(request, *args, **kwargs)
    

class LabelListView(LoginRequiredMixin, ListView):
    model = Label
    template_name = 'labels/index.html'
    context_object_name = 'labels'


class LabelCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = 'labels/create.html'
    success_url = reverse_lazy('labels_index')
    success_message = _('Метка успешно создана')


class LabelUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = 'labels/update.html'
    success_url = reverse_lazy('labels_index')
    success_message = _('Метка успешно изменена')


class LabelDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Label
    template_name = 'labels/delete.html'
    success_url = reverse_lazy('labels_index')
    success_message = _('Метка успешно удалена')

    def post(self, request, *args, **kwargs):
        label = self.get_object()
        try:
            if label.tasks.exists():
                messages.error(request, _('Невозможно удалить метку, связанную с задачами'))
                return redirect('labels_index')

            messages.success(request, self.success_message)
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _('Невозможно удалить метку, связанную с задачами'))
            return redirect('labels_index')