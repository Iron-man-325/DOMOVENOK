.. toctree::
   :maxdepth: 2
   :caption: Документация:

   views

.. _views_module:

views.py
========

Модуль содержит все Django-представления (views) проекта. Здесь реализована логика обработки HTTP-запросов, авторизации, работы с квартирами и профилями пользователей.

.. contents:: Содержание
   :depth: 2
   :local:

Основные функции
----------------

.. py:function:: get_base_context(pagename: str = "", **kwargs)

   Формирует базовый контекст для шаблонов.

   :param str pagename: Название страницы (для тега ``<title>``)
   :param kwargs: Дополнительные ключи контекста
   :return: Словарь контекста с меню и переданными параметрами
   :rtype: dict

   Пример использования::

      context = get_base_context("Главная", form=MyForm())

.. py:function:: parse(s)

   Вспомогательная функция для очистки строк от символов ``[``, ``]``, ``"``.

   :param str s: Входная строка
   :return: Очищенная строка
   :rtype: str

Представления (Views)
---------------------

Аутентификация
~~~~~~~~~~~~~~

.. py:function:: login_page(request)

   Обрабатывает страницу входа пользователя.

   :param request: WSGIRequest
   :return: HttpResponse с формой авторизации или редирект на профиль
   :raises: Http404 при ошибках

.. py:function:: registration_page(request)

   Обрабатывает регистрацию новых пользователей.

   :param request: WSGIRequest
   :return: HttpResponse с формой регистрации или редирект на профиль

Работа с квартирами
~~~~~~~~~~~~~~~~~~~

.. py:function:: flat_list(request)

   Отображает список всех квартир.

   :param request: WSGIRequest
   :return: HttpResponse со списком квартир

.. py:function:: add_apartment(request)

   Добавление новой квартиры (только для авторизованных пользователей).

   :param request: WSGIRequest
   :return: HttpResponse с формой или редирект на список квартир
   :decorators: login_required

.. py:function:: show_flat(request, flat_id)

   Детальная страница квартиры.

   :param request: WSGIRequest
   :param int flat_id: ID квартиры
   :return: HttpResponse с данными квартиры или 404
   :decorators: login_required

Профиль пользователя
~~~~~~~~~~~~~~~~~~~~

.. py:function:: profile_page(request)

   Главная страница профиля пользователя.

   :param request: WSGIRequest
   :return: HttpResponse с данными профиля
   :decorators: login_required

.. py:function:: redact_profile(request)

   Редактирование профиля пользователя.

   :param request: WSGIRequest
   :return: HttpResponse с формами редактирования
   :decorators: login_required

Поддержка
~~~~~~~~~

.. py:function:: send_support_message(request)

   Обработчик отправки сообщений в поддержку (CSRF-exempt).

   :param request: WSGIRequest
   :return: JsonResponse с результатом операции
   :decorators: csrf_exempt

.. py:function:: my_support_requests(request)

   Просмотр своих запросов в поддержку.

   :param request: WSGIRequest
   :return: HttpResponse со списком запросов
   :decorators: login_required

FAQ
~~~

.. py:function:: faq_questions(request)

   Страница с часто задаваемыми вопросами.

   :param request: WSGIRequest
   :return: HttpResponse со списком вопросов-ответов

Дополнительно
~~~~~~~~~~~~~

.. py:function:: adminn(request)

   Панель администратора (просмотр всех квартир).

   :param request: WSGIRequest
   :return: HttpResponse со списком квартир
   :decorators: login_required

Классы контекста
----------------

.. py:class:: MenuUrlContext(url_name: str, name: str)

   Вспомогательный класс для формирования меню.

   :param str url_name: Имя URL-пути
   :param str name: Отображаемое название

.. py:class:: Question(q: str, a: str = "")

   Класс для вопросов/ответов в FAQ.

   :param str q: Текст вопроса
   :param str a: Текст ответа (опционально)