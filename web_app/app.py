import json
from flask import Flask, render_template, abort

app = Flask(__name__)

DATA_FILE = 'avito_apartments_sdam_high_res_photos.json' 
try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        apartments_data = json.load(f)
    print(f"Успешно загружено {len(apartments_data)} записей из {DATA_FILE}")
except FileNotFoundError:
    print(f"Ошибка при загрузке данных: Файл '{DATA_FILE}' не найден. Запустите парсер для его создания.")
    apartments_data = []
except json.JSONDecodeError:
    print(f"Ошибка при загрузке данных: Не удалось прочитать JSON из файла '{DATA_FILE}'. Проверьте его формат онлайн-валидатором.")
    apartments_data = []
except Exception as e:
    print(f"Неожиданная ошибка при загрузке данных из файла '{DATA_FILE}': {e}")
    apartments_data = []


apartments_dict = {apt.get('id'): apt for apt in apartments_data if apt.get('id')}
if len(apartments_data) != len(apartments_dict):
    print("Предупреждение: В данных найдены записи без 'id' или с дублирующимися 'id'.")


@app.route('/')
def list_apartments():
    return render_template('list.html', apartments=apartments_data)


@app.route('/apartment/<apartment_id>')
def view_apartment_detail(apartment_id):
    """Маршрут для отображения детальной информации по ID квартиры."""
    apartment = apartments_dict.get(apartment_id)

    if not apartment:
        abort(404)

    return render_template('detail.html', apartment=apartment)

@app.errorhandler(404)
def page_not_found(error):
    """Обработчик ошибки 404 Not Found."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)