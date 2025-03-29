import requests
import json

CLIENT_ID = "наш клиент айди"
CLIENT_SECRET = "наш клиент секрет"
ACCESS_TOKEN = "наш токен доступа, полученный через QAuth" 

# Получение объявления о недвижимости
def get_realty_ads():
    url = "https://api.avito.ru/core/v1/items"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "category_id": REALTY_CATEGORY_ID,
        "status": "active"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

# Создать объявление о продаже квартиры(если будем лопатиться с тем, чтобы все квартиры с нашего сайта оказывались на авито автоматически)
def create_apartment_ad(
    title: str,
    description: str,
    price: int,
    address: str,
    rooms: int,
    square: int,
    floor: int,
    total_floors: int
):
    url = "https://api.avito.ru/core/v1/items"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": title,
        "description": description,
        "price": price,
        "category_id": APARTMENTS_SUBCATEGORY_ID,
        "address": address,
        "params": [
            {"name": "rooms", "value": str(rooms)},
            {"name": "square", "value": str(square)},
            {"name": "floor", "value": str(floor)},
            {"name": "total_floors", "value": str(total_floors)}
        ],
        "coordinates": {
            "latitude": "координаты", 
            "longitude": "координаты"
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

# Пример использования
#if __name__ == "__main__":
    # Получить объявления о недвижимости
    #realty_ads = get_realty_ads()
    #if realty_ads:
        #print("Объявления о недвижимости:")
        #print(json.dumps(realty_ads, indent=2, ensure_ascii=False))

    # Создать новое объявление
    #new_ad = create_apartment_ad(
        #title="Продажа 2-комнатной квартиры",
        #description="Светлая квартира в центре...",
        #price=10_000_000,
        #address="Москва, Тверская ул., 10",
        #rooms=2,
        #square=65,
        #floor=5,
        #total_floors=9
    #)
    #if new_ad:
        #print("Новое объявление создано:")
        #print(json.dumps(new_ad, indent=2, ensure_ascii=False))