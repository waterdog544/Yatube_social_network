# YATUBE_SOCIAL_NETWORK

Социальная сеть для публикации сообщений, фотографий и получения комментариев от других пользователей.

## Технологии

Python 3.7

Django 2.2.19

HTML

CSS (Bootstrap)

Unittest

## Как запустить проект

Сделать fork репозитория <https://github.com/waterdog544/Yatube_social_network>

Клонировать репозитории

```text
git clone <https://github.com/username/Yatube_social_network>
```

Установить и активировать виртуальное окружение

```text
python -m venv venv
source venv/bin/activate
```

Установить зависимости

```text
pip install -r requirements.txt
```

Выполнить миграции и запустить сервер

```text
python manage.py migrate
python manage.py runserver
```

## Функционал сайта

### Подключен интерфейс администратора сайта

### Для пользователей сайта реализован выбор сообщений

- определенного автора
- определенной группы

### Зарегистрированные пользователи могут

- публиковать сообщения
- подписываться на любимого автора
- комментировать понравившихся записей

### Выполняется оптимизация

- постраничное разбиение материалов
- кеширование части шаблона

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
