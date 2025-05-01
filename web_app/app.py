import json
from flask import Flask, render_template, abort

app = Flask(__name__)

# Имя файла с данными, который генерирует ваш парсер
DATA_FILE = 'avito_apartments_sdam_all_optimized.json'

# Загружаем данные из JSON файла при запуске приложения
# В более сложных приложениях может потребоваться кэширование или загрузка по требованию
try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        apartments_data = json.load(f)
except FileNotFoundError:
    print(f"Ошибка: Файл данных '{DATA_FILE}' не найден.")
    apartments_data = []
except json.JSONDecodeError:
    print(f"Ошибка: Не удалось прочитать JSON из файла '{DATA_FILE}'. Проверьте его формат.")
    apartments_data = []

# Преобразуем список данных в словарь для быстрого доступа по ID
apartments_dict = {apt.get('id'): apt for apt in apartments_data if apt.get('id')}


@app.route('/')
def list_apartments():
    """Маршрут для отображения списка квартир."""
    # Передаем список всех квартир в шаблон list.html
    return render_template('list.html', apartments=apartments_data)


@app.route('/apartment/<apartment_id>')
def view_apartment_detail(apartment_id):
    """Маршрут для отображения детальной информации по ID квартиры."""
    # Ищем квартиру по ID в словаре
    apartment = apartments_dict.get(apartment_id)

    # Если квартира не найдена, показываем ошибку 404
    if not apartment:
        abort(404)

    # Передаем данные конкретной квартиры в шаблон detail.html
    return render_template('detail.html', apartment=apartment)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404 # Опционально: создайте шаблон 404.html


if __name__ == '__main__':
    # Убедитесь, что debug=False для продакшена
    app.run(debug=True)