.. _models_module:

models.py
=========

.. contents:: Содержание
   :depth: 2
   :local:

Основные модели
---------------

Account
~~~~~~~

.. py:class:: Account(models.Model)

   Модель банковского счета пользователя.

   **Поля:**

   - ``user`` (ForeignKey): Связь с пользователем
   - ``currency`` (CharField): Валюта счета (USD, EUR, RUB, KZT)
   - ``balance`` (DecimalField): Баланс счета (не может быть отрицательным)
   - ``created_at`` (DateTimeField): Дата создания
   - ``is_active`` (BooleanField): Активен ли счет

   **Методы:**

   .. py:method:: deposit(amount, description="")

      Пополнение счета.

      :param amount: Сумма пополнения
      :param description: Описание операции
      :raises ValueError: Если сумма <= 0
      :return: Новый баланс

   .. py:method:: withdraw(amount, description="")

      Снятие средств со счета.

      :param amount: Сумма снятия
      :param description: Описание операции
      :raises ValueError: Если сумма <= 0 или недостаточно средств
      :return: Новый баланс

   **Meta:**

   - ``unique_together``: У пользователя может быть только один счет в каждой валюте
   - ``ordering``: Сортировка по дате создания (новые сначала)

Transaction
~~~~~~~~~~~

.. py:class:: Transaction(models.Model)

   Модель финансовой транзакции.

   **Типы транзакций (TRANSACTION_TYPE_CHOICES):**

   - deposit - Пополнение
   - withdrawal - Снятие
   - transfer_in - Входящий перевод
   - transfer_out - Исходящий перевод
   - payment - Платеж
   - refund - Возврат средств

   **Статусы (STATUS_CHOICES):**

   - pending - В обработке
   - completed - Завершено
   - failed - Ошибка
   - cancelled - Отменено

   **Поля:**

   - ``account``: Связанный счет
   - ``amount``: Сумма транзакции
   - ``transaction_type``: Тип транзакции
   - ``description``: Описание
   - ``status``: Статус (по умолчанию "pending")
   - ``created_at``: Дата создания
   - ``completed_at``: Дата завершения

   **Meta:**

   - ``ordering``: Сортировка по дате (новые сначала)
   - ``indexes``: Индексы для ускорения запросов

Apartment
~~~~~~~~~

.. py:class:: Apartment(models.Model)

   Модель квартиры для аренды.

   **Основные поля:**

   - ``user``: Владелец квартиры
   - ``city``, ``street``, ``housenum``: Адрес
   - ``description``: Описание
   - ``image``: Фото квартиры

   **Характеристики:**

   - ``max_people``: Макс. количество гостей
   - ``sleeping_places``: Количество спальных мест
   - ``bathrooms``: Количество санузлов
   - ``square``: Площадь (м²)
   - ``cost_per_night``: Стоимость за ночь
   - ``prepayment``: Предоплата
   - ``min_nights``: Минимальный срок аренды

Profile
~~~~~~~

.. py:class:: Profile(models.Model)

   Профиль пользователя (расширение стандартной модели User).

   **Поля:**

   - ``user``: Связь 1-to-1 с User
   - ``avatar``: Аватар пользователя

Вспомогательные модели
----------------------

ViewHistory
~~~~~~~~~~~

.. py:class:: ViewHistory(models.Model)

   История просмотров квартир пользователями.

   **Поля:**

   - ``user``: Пользователь
   - ``apartment``: Просмотренная квартира
   - ``viewed_at``: Время просмотра

   **Meta:**

   - ``unique_together``: Запрет дублирования записей
   - ``ordering``: Сортировка по времени (новые сначала)

StaticInput
~~~~~~~~~~~

.. py:class:: StaticInput(models.Model)

   Модель для хранения показаний счетчиков и квитанций.

   **Поля:**

   - Водоснабжение (``water_*``)
   - Электричество (``electro_*``)
   - Газ (``gas_*``)
   - Аренда (``rent_*``)
   - ГКХ (``GKX_*``)
   - Все поля имеют:
     - ``_input``: Показания счетчика
     - ``_payment``: Сумма платежа
     - ``_receipt``: Скан квитанции

Rent_Apartment
~~~~~~~~~~~~~~

.. py:class:: Rent_Apartment(models.Model)

   Модель аренды квартиры.

   **Поля:**

   - ``landlord``: Арендодатель
   - ``tenant``: Арендатор
   - ``apartment``: Квартира
   - ``price``: Цена аренды
   - ``dates``: Срок аренды
   - ``status``: Статус аренды

SupportRequest
~~~~~~~~~~~~~~

.. py:class:: SupportRequest(models.Model)

   Запросы в поддержку.

   **Поля:**

   - ``user``: Пользователь
   - ``message``: Текст сообщения
   - ``photo1``, ``photo2``, ``photo3``: Прикрепленные фото
   - ``created_at``: Время создания

   **Методы:**

   .. py:method:: photos()

      Возвращает список прикрепленных фото.

      :return: Список непустых фото

ExchangeRate
~~~~~~~~~~~~

.. py:class:: ExchangeRate(models.Model)

   Курсы валют.

   **Поля:**

   - ``from_currency``: Исходная валюта
   - ``to_currency``: Целевая валюта
   - ``rate``: Курс обмена
   - ``updated_at``: Время обновления

PaymentMethod
~~~~~~~~~~~~~

.. py:class:: PaymentMethod(models.Model)

   Платежные методы пользователя.

   **Типы методов (METHOD_TYPE_CHOICES):**

   - card - Банковская карта
   - bank_account - Банковский счет
   - ewallet - Электронный кошелек
   - crypto - Криптовалюта

   **Поля:**

   - ``user``: Владелец метода
   - ``method_type``: Тип метода
   - ``details``: Детали (хранятся в JSON)
   - ``is_default``: Метод по умолчанию