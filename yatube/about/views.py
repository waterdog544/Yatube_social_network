# from django.shortcuts import render
from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_title'] = 'Об авторе проекта'
        context['author_head'] = 'Об авторе проекта'
        context['author_text'] = ('Привет. Я - Шванов Андрей. Занимаюсь '
                                  'изучением программирования на языке '
                                  'Python. Разрабатываю backend '
                                  'сайтов с использованием Django.')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tech_title'] = 'Технологии'
        context['tech_text'] = ('Для создания сайта применяется ORM Django.'
                                'Backend написан на Python 3.7.')
        return context
