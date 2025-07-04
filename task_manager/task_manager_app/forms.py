from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Status, Task, Label


class UserChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        full_name = obj.get_full_name()
        if full_name:
            return f"{full_name}"
        return obj.username


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя'})
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'})


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('Имя'),
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    last_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('Фамилия'),
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = _('Имя пользователя')
        self.fields['password1'].label = _('Пароль')
        self.fields['password2'].label = _('Подтверждение пароля')
        self.fields['password1'].help_text = _(
            'Ваш пароль должен содержать как минимум 3 символа.')
        self.fields['password2'].help_text = _(
            'Введите тот же пароль, что и раньше, для подтверждения.')


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'}, render_value=False
        ),
        label=_('Пароль'),
        help_text=_('Ваш пароль должен содержать как минимум 3 символа.'),
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'}, render_value=False
        ),
        label=_('Подтверждение пароля'),
        help_text=_('Введите тот же пароль, что и раньше, для подтверждения.'),
        required=True
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError(
                'Имя пользователя является обязательным полем.')

        if len(username) > 150:
            raise ValidationError(
                'Имя пользователя не может быть длиннее 150 символов.')

        import re
        if not re.match(r'^[a-zA-Z0-9@./+\-_]+$', username):
            # ▼▼▼ ЭТА СТРОКА БЫЛА СЛИШКОМ ДЛИННОЙ, Я ЕЕ РАЗДЕЛИЛ ▼▼▼
            raise ValidationError(
                'Имя пользователя может содержать только буквы, цифры и '
                'символы @/./+/-/_.'
            )

        if self.instance.username != username:
            if User.objects.filter(username=username).exists():
                raise ValidationError(
                    'Пользователь с таким именем уже существует.')
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name or not first_name.strip():
            raise ValidationError('Имя является обязательным полем.')
        return first_name.strip()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name or not last_name.strip():
            raise ValidationError('Фамилия является обязательным полем.')
        return last_name.strip()

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise ValidationError('Пароль является обязательным полем.')

        if len(password1) < 3:
            raise ValidationError('Пароль должен содержать минимум 3 символа.')

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if not password2:
            raise ValidationError(
                'Подтверждение пароля является обязательным полем.')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Имя'),
        }


class TaskForm(forms.ModelForm):
    executor = UserChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_('Исполнитель'),
        widget=forms.Select(attrs={'class': 'form-select'}))

    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label=_('Метки')
    )

    class Meta:
        model = Task
        fields = ('name', 'description', 'status', 'executor', 'labels')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': _('Имя')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4, 'placeholder': _('Описание')
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': _('Имя'),
            'description': _('Описание'),
            'status': _('Статус'),
            'labels': _('Метки'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['executor'].empty_label = "---------"


class LabelForm(forms.ModelForm):
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
            'name': _('Имя'),
        }