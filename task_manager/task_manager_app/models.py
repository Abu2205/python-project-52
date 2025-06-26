from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Status(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_('Name')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )

    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')
        ordering = ['created_at']

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name=_('Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        verbose_name=_('Status')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='authored_tasks',
        verbose_name=_('Author')
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='assigned_tasks',
        blank=True,
        null=True,
        verbose_name=_('Executor')
    )
    labels = models.ManyToManyField(
        'Label',
        related_name='tasks',
        blank=True,
        verbose_name=_('Labels')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name=_("Name")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created at")
    )

    def __str__(self):
        return self.name