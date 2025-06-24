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
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Статус")
    )
    
    # ==================== НАЧАЛО ИЗМЕНЕНИЙ ====================
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label=_("Исполнитель"),
        # Указываем, как отображать каждого пользователя в списке
        field_name='executor',
        label_from_instance=lambda obj: obj.get_full_name()
    )
    # ===================== КОНЕЦ ИЗМЕНЕНИЙ =====================

    labels = django_filters.ModelChoiceFilter(
        field_name='labels',
        queryset=Label.objects.all(),
        empty_label="---------",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("Метка")
    )

    self_tasks = django_filters.BooleanFilter(
        method='filter_author_tasks',
        label=_("Только свои задачи"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Task
        # Убрал 'label' и 'self_tasks' отсюда, т.к. они определены выше вручную
        fields = ['status', 'executor'] 

    def filter_author_tasks(self, queryset, name, value):
        """Фильтр для отображения только задач текущего пользователя"""
        if value and self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)
        return queryset