import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Task, Status, Label


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
        label="Исполнитель"
    )
    

    label = django_filters.ModelChoiceFilter(
        field_name='labels',
        queryset=Label.objects.all(),
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-select mr-3 ml-2'}),
        label="Метка"
    )

    self_tasks = django_filters.BooleanFilter(
        method='filter_author_tasks',
        label="Только свои задачи",
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