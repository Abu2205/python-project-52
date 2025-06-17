from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Status, Task, Label


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('First name'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('Last name'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Обновляем labels и help_text для соответствия требованиям
        self.fields['username'].label = _('Username')
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Password confirmation')
        self.fields['password1'].help_text = _(
            'Your password must contain at least 3 characters.'
        )
        self.fields['password2'].help_text = _(
            'Enter the same password as before, for verification.'
        )


class UserUpdateForm(forms.ModelForm):
    """Форма обновления пользователя"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'username': _('Username'),
        }


class StatusForm(forms.ModelForm):
    """Форма для статуса"""
    
    class Meta:
        model = Status
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Name'),
        }


class TaskForm(forms.ModelForm):
    """Форма для задачи"""
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label=_('Labels')
    )

    class Meta:
        model = Task
        fields = ('name', 'description', 'status', 'executor', 'labels')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'executor': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': _('Name'),
            'description': _('Description'),
            'status': _('Status'),
            'executor': _('Executor'),
            'labels': _('Labels'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['executor'].empty_label = _('Select executor')
        self.fields['executor'].required = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем пустой вариант для исполнителя
        self.fields['executor'].empty_label = _('Select executor')
        self.fields['executor'].required = False

# В файле task_manager_app/forms.py исправьте LabelForm:

class LabelForm(forms.ModelForm):
    """Форма для меток"""
    
    class Meta:
        model = Label
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя',
                'maxlength': '100',
                'required': True
            }),
        }
        labels = {
            'name': _('Name'),  # Это будет переведено как "Имя"
        }
