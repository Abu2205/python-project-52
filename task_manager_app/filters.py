# task_manager_app/filters.py
import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Task, Status, Label


class UserChoiceField(forms.ModelChoiceField):
    """Кастомное поле для отображения пользователей"""
    
    def label_from_instance(self, obj):
        """Определяет, как отображать каждого пользователя в select"""
        full_name = obj.get_full_name()
        if full_name:
            return f"{full_name}"
        return obj.username


class TaskFilter(django_filters.FilterSet):
    """Фильтр для задач"""
    
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-select ml-2 mr-3'}),
        label="Статус"
    )
    
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-select mr-3 ml-2'}),
        label="Исполнитель",
        field_class=UserChoiceField
    )
    
    # Используем имя label вместо labels для соответствия тесту
    label = django_filters.ModelChoiceFilter(
        field_name='labels',  # Указываем реальное поле модели
        queryset=Label.objects.all(),
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-select mr-3 ml-2'}),
        label="Метка"  # Используем русский текст напрямую
    )
    
    # Изменяем имя поля с author_tasks на self_tasks
    self_tasks = django_filters.BooleanFilter(
        method='filter_author_tasks',
        label="Только свои задачи",  # Используем русский текст напрямую
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input mr-3'})
    )

    class Meta:
        model = Task
        fields = ['status', 'executor', 'label', 'self_tasks']

    def filter_author_tasks(self, queryset, name, value):
        """Фильтр для отображения только задач текущего пользователя"""
        if value and self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)
        return queryset