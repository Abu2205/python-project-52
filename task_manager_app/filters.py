import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Task, Status, Label


class TaskFilter(django_filters.FilterSet):
    """Фильтр для задач"""
    
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        empty_label=_("All"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        empty_label=_("All"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        empty_label=_("All"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    author_tasks = django_filters.BooleanFilter(
        method='filter_author_tasks',
        label=_("Only my tasks"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels', 'author_tasks']

    def filter_author_tasks(self, queryset, name, value):
        """Фильтр для отображения только задач текущего пользователя"""
        if value and self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)
        return queryset