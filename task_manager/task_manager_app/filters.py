import django_filters
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Task, Status, Label


class TaskFilter(django_filters.FilterSet):

    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label=_("Статус"),
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label=_("Исполнитель"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        label=_("Метка"),
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    self_tasks = django_filters.BooleanFilter(
        method='filter_author_tasks',
        label=_("Только свои задачи"),
        widget=forms.CheckboxInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        executor_field = self.filters['executor'].field
        executor_field.label_from_instance = lambda obj: obj.get_full_name()
        executor_field.empty_label = "---------"

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels']

    def filter_author_tasks(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)
        return queryset