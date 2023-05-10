# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

# Социальная сеть yatube
Предоставляет функционал для создания и комментирования постов, подписки на авторов.
### Технологии :
Python 3.7 
Django 2.2.19

### Функционал проекта: 
- Регистрация пользователей по уникальному коду, высылаемому по почте;
- подписка на авторов и отображение их постов в отдельной ленте;
- комментирование постов;
- поиск постов;
- кеширование главной страницы;
- паджинация.

### Запуск проекта в dev-режиме 
- Установите и активируйте виртуальное окружение: ```python -m venv venv```
- Установите зависимости из файла requirements.txt: ``` pip install -r requirements.txt ``` 
- Создайте миграции и мигрируйте их в БД: ```python manage.py makemigrations```, ```python manage.py migrate```
-  Запустите сервер, выполнив в папке с файлом manage.py команду: ``` python manage.py runserver ``` 
