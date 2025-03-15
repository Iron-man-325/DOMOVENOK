import requests
import json
import time

terminal_key = 'ключ-терминала'
secret_key = 'наш-ключ'
amount = 10000  # Сумма в копейках (будем брать из бдшки к которой подключим счетчики и саму арендную стоимость квартиры)
order_id = 'ORDER_ID'  # Уникальный идентификатор заказа
description = 'Описание платежа' # ТОже пуллим из бд сайта+счетчиков

# линк для создания запроса на платеж
url = 'https://securepay.tinkoff.ru/v2/Init'

# Данные для запроса
data = {
    "TerminalKey": terminal_key,
    "Amount": amount,
    "OrderId": "order_id_" + str(int(time.time())), # Генерация уникального ID, используя текущее время
    "Description": description,
    "DATA": {
        "Email": "customer@example.com"  # Email клиента из бд сайта
    },
    "Items":[
        # Тут будет все то, за что платят деньги - квартплата, жку и тп.
    ]
}

# Подпись запроса
import hashlib
import hmac

def generate_signature(data, secret_key):
    json_data = json.dumps(data, separators=(',', ':'))
    return hmac.new(secret_key.encode(), json_data.encode(), hashlib.sha256).hexdigest()

# Добавляем подпись к данным
data['Token'] = generate_signature(data, secret_key)

# Отправляем запрос
response = requests.post(url, json=data)

# Обрабатываем ответ
if response.status_code == 200:
    response_data = response.json()
    print("Response:", response_data)
else:
    print("Error:", response.status_code, response.text)
