from django.views.generic import TemplateView


class IndexView(TemplateView):
    """Главная страница с приветствием"""
    template_name = 'index.html'