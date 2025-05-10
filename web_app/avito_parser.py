import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.avito.ru/moskva/kvartiry/sdam"
OUTPUT_JSON_FILE = 'avito_apartments.json'
WAIT_TIMEOUT_LIST = 15
WAIT_TIMEOUT_DETAIL = 20

MAX_PAGES_TO_PARSE = None

MAX_APARTMENTS_TO_SCRAPE = None

SCROLL_PAUSE_TIME = 1.5
SCROLL_INCREMENT_RATIO = 0.8
SCROLL_TOLERANCE = 10
PAUSE_AFTER_NEW_ITEM_FOUND_LIST = 0.5

PAUSE_BETWEEN_DETAIL_PAGES = 1.5

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    chrome_options.add_argument("--start-maximized")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Ошибка при настройке драйвера: {e}")
        return None

def parse_floor_info(title_text):
    match = re.search(r'(\d+)/(\d+)\s+эт', title_text)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return "N/A"

def parse_rooms_info(title_text):
    room_match = re.search(r'(\d+)-к', title_text)
    if room_match:
        return room_match.group(1)
    if "студия" in title_text.lower():
         return "Студия"
    if "комната" in title_text.lower():
         return "Комната"
    return "N/A"

def parse_area_info(title_text):
    match = re.search(r'(\d+[\,\.]?\d*)\s*м²', title_text)
    if match:
        return match.group(1).replace(',', '.')
    return "N/A"

def parse_address_parts(full_address):
    city = None
    street = None
    housenum = None

    parts = [p.strip() for p in full_address.replace(',', ' ').split()]

    if not parts:
        return None, None, None

    if len(parts) > 0:
        city = parts[0]

    if len(parts) > 1:
        house_match = re.search(r'\d+[а-я]?$', parts[-1])
        if house_match:
            housenum = parts[-1]
            street_parts = parts[1:-1]
            street = ' '.join(street_parts) if street_parts else None
        elif len(parts) > 1:
             street_parts = parts[1:]
             street = ' '.join(street_parts)
             housenum = None

    return city if city and city != 'N/A' else None, \
           street if street and street != 'N/A' else None, \
           housenum if housenum and housenum != 'N/A' else None

def parse_number(text_value):
    if isinstance(text_value, (int, float)):
        return text_value
    if not isinstance(text_value, str):
        return None

    cleaned_text = re.sub(r'[^\d.,]', '', text_value)
    cleaned_text = cleaned_text.replace(',', '.')

    try:
        if '.' in cleaned_text:
            return float(cleaned_text)
        else:
             return int(cleaned_text)
    except ValueError:
        return None


def extract_from_characteristics(characteristics_dict, keys):
    if not characteristics_dict:
        return None
    for key in keys:
        if key in characteristics_dict and characteristics_dict[key] and characteristics_dict[key].strip() not in ('N/A', ''):
            return characteristics_dict[key].strip()
    return None

def parse_numeric_characteristic(characteristics_dict, keys):
    value = extract_from_characteristics(characteristics_dict, keys)
    if value:
        return parse_number(value)
    return None


def scrape_listing_page(driver):
    all_page_data = []
    processed_item_ids = set()

    time.sleep(3)

    try:
        items_container_selector = 'div[data-marker="catalog-serp"]'
        WebDriverWait(driver, WAIT_TIMEOUT_LIST).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, items_container_selector))
        )

        last_scroll_position = -1
        scroll_attempts = 0

        while True:
            scroll_attempts += 1
            try:
                WebDriverWait(driver, 5).until(
                     EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="item"]'))
                )
                listing_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-marker="item"]')
            except (TimeoutException, StaleElementReferenceException):
                 listing_elements = []

            current_items_on_page_count = len(listing_elements)
            new_items_found_in_scroll = 0
            parsed_in_this_scroll = []

            current_scroll_items_to_process = []
            for item in listing_elements:
                 try:
                     item_id = item.get_attribute('data-item-id')
                     if item_id and item_id not in processed_item_ids:
                          current_scroll_items_to_process.append((item_id, item))
                          processed_item_ids.add(item_id)
                 except StaleElementReferenceException:
                      pass
                 except Exception as e:
                     pass

            new_items_found_in_scroll = len(current_scroll_items_to_process)
            if new_items_found_in_scroll > 0:
                 pass


            for item_id, item in current_scroll_items_to_process:
                    time.sleep(PAUSE_AFTER_NEW_ITEM_FOUND_LIST)

                    data = {
                        'id': item_id,
                        'наименование': 'N/A',
                        'количество_комнат': 'N/A',
                        'общая_площадь_м2': 'N/A',
                        'этаж_инфо': 'N/A',
                        'ссылка': 'N/A',
                        'фотографии_список': []
                    }

                    try:
                        title_element = item.find_element(By.CSS_SELECTOR, 'a[data-marker="item-title"]')
                        raw_title = title_element.text.strip()
                        data['наименование'] = raw_title
                        data['ссылка'] = title_element.get_attribute('href')
                        data['количество_комнат'] = parse_rooms_info(raw_title)
                        data['этаж_инфо'] = parse_floor_info(raw_title)
                        data['общая_площадь_м2'] = parse_area_info(raw_title)
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                         pass

                    try:
                        photo_elements = item.find_elements(By.CSS_SELECTOR, 'li[data-marker="slider-image/image-wrapper"] img, img[class*="photo-slider-image"], img[itemprop="image"]')
                        for photo in photo_elements:
                            try:
                                src = photo.get_attribute('data-src') or photo.get_attribute('src')
                                if src and not src.startswith('data:image'):
                                     if src.startswith('//'): src = 'https:' + src
                                     elif src.startswith('/'): src = 'https://www.avito.ru' + src
                                     if src not in data['фотографии_список']:
                                        data['фотографии_список'].append(src)
                            except StaleElementReferenceException: pass
                            except Exception as e_photo: pass

                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        pass

                    parsed_in_this_scroll.append(data)


            if parsed_in_this_scroll:
                 all_page_data.extend(parsed_in_this_scroll)


            current_scroll_position = driver.execute_script("return window.pageYOffset;")
            viewport_height = driver.execute_script("return window.innerHeight;")
            document_height = driver.execute_script("return document.body.scrollHeight;")

            scroll_by = int(viewport_height * SCROLL_INCREMENT_RATIO)
            if current_scroll_position + viewport_height + scroll_by >= document_height:
                 scroll_by = document_height - (current_scroll_position + viewport_height) + 50
                 if scroll_by <= 0:
                     scroll_by = 0

            driver.execute_script(f"window.scrollBy(0, {scroll_by});")

            time.sleep(SCROLL_PAUSE_TIME)

            new_scroll_position = driver.execute_script("return window.pageYOffset;")
            new_document_height = driver.execute_script("return document.body.scrollHeight;")

            try:
                updated_listing_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-marker="item"]')
                updated_items_count = len(updated_listing_elements)
            except StaleElementReferenceException:
                 updated_items_count = current_items_on_page_count


            item_count_not_increasing = updated_items_count <= current_items_on_page_count
            scroll_position_not_changing = abs(new_scroll_position - last_scroll_position) < SCROLL_TOLERANCE


            if new_items_found_in_scroll == 0 or (scroll_position_not_changing and item_count_not_increasing):
                 break

            at_very_bottom = (current_scroll_position + viewport_height) >= document_height - SCROLL_TOLERANCE - 50
            if new_items_found_in_scroll > 0 and scroll_position_not_changing and not at_very_bottom:
                 break


            last_scroll_position = new_scroll_position


    except TimeoutException:
        print("Время ожидания загрузки основного контейнера списка истекло.")
    except Exception as e:
        print(f"Произошла ошибка при парсинге страницы списка: {e}")

    print(f"Парсинг страницы списка завершен. Собрано {len(all_page_data)} уникальных базовых записей с этой страницы.")
    return all_page_data

def parse_srcset(srcset_string):
    if not srcset_string:
        return None

    candidates = []
    pairs = [pair.strip() for pair in srcset_string.split(',')]

    for pair in pairs:
        parts = pair.split()
        if len(parts) == 2:
            url = parts[0]
            descriptor = parts[1]
            match = re.match(r'(\d+(\.\d+)?)([xw])', descriptor)
            if match:
                value = float(match.group(1))
                unit = match.group(3)
                candidates.append({'url': url, 'value': value, 'unit': unit})
            else:
                candidates.append({'url': url, 'value': 1.0, 'unit': 'x'})
        elif len(parts) == 1:
             candidates.append({'url': parts[0], 'value': 1.0, 'unit': 'x'})


    if not candidates:
        return None

    candidates.sort(key=lambda x: (x['unit'] == 'x', x['value']), reverse=True)

    return candidates[0]['url'] if candidates else None

def scrape_apartment_detail(driver, listing_url):
    apartment_data = {
        'avito_id': 'N/A',
        'avito_link': listing_url,
        'name': 'N/A',
        'city': None,
        'street': None,
        'stage': None,
        'number': None,
        'housenum': None,
        'description': 'N/A',
        'max_people': None,
        'sleeping_places': None,
        'sleeping_rooms': None,
        'bathrooms': None,
        'square': None,
        'cost_per_night': None,
        'prepayment': None,
        'min_nights': None,
        'free_at': None,
        'nearby_objects': '[]',
        'amenities': '[]',
        'living_rules': '[]',
        'image_url': None,
        'original_avito_data': {}
    }

    try:
        driver.get(listing_url)
        WebDriverWait(driver, WAIT_TIMEOUT_DETAIL).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item-view/item-price"]'))
        )
        time.sleep(1)

        if apartment_data['avito_link'] and 'avito.ru' in apartment_data['avito_link']:
             id_match = re.search(r'_(\d+)$', apartment_data['avito_link'])
             if id_match:
                  apartment_data['avito_id'] = id_match.group(1)

        try:
            title_element = driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/title"]')
            apartment_data['name'] = title_element.text.strip()
        except NoSuchElementException: pass

        try:
            description_element = driver.find_element(By.CSS_SELECTOR, '[itemprop="description"]')
            apartment_data['description'] = description_element.text.strip()
        except NoSuchElementException: pass

        price_value = 'N/A'
        try:
            try:
                price_element_for_attr = driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-price"]')
                content_attr = price_element_for_attr.get_attribute('content')
                if content_attr:
                     price_value = content_attr.strip()
            except NoSuchElementException: pass

            if price_value == 'N/A':
                 try:
                      price_element_for_text = driver.find_element(By.CSS_SELECTOR, '#bx_item-price-value')
                      text_content = price_element_for_text.text.strip()
                      if text_content:
                           price_value = text_content
                 except NoSuchElementException: pass

            apartment_data['cost_per_night'] = parse_number(price_value) if price_value != 'N/A' else None

        except Exception as e:
            pass


        try:
             deposit_fee_element = driver.find_element(By.CSS_SELECTOR, '.styles-item-price-sub-price-A1IZy span')
             deposit_fee_text = deposit_fee_element.text.strip()

             deposit_match = re.search(r'залог\s*([\d\s]+)\s*₽', deposit_fee_text)
             if deposit_match:
                  deposit_value_str = deposit_match.group(1).replace('\xa0', '').replace(' ', '').strip()
                  apartment_data['prepayment'] = parse_number(deposit_value_str)

        except NoSuchElementException: pass
        except Exception as e:
            pass


        full_address = 'N/A'
        try:
            address_element = driver.find_element(By.CSS_SELECTOR, '[itemprop="address"] .style-item-address__string-wt61A')
            full_address = address_element.text.strip()
            apartment_data['original_avito_data']['адрес'] = full_address

            city, street, housenum = parse_address_parts(full_address)
            apartment_data['city'] = city
            apartment_data['street'] = street
            apartment_data['housenum'] = housenum

        except NoSuchElementException: pass

        try:
            metro_elements = driver.find_elements(By.CSS_SELECTOR, '[itemprop="address"] .style-item-address-georeferences-item-TZsrp')
            metro_info = [el.text.strip() for el in metro_elements if el.text.strip()]
            apartment_data['original_avito_data']['метро'] = ", ".join(metro_info) if metro_info else "N/A"
        except NoSuchElementException: pass


        characteristics_dict = {}
        try:
            characteristics_container = driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-params"]')
            char_elements = characteristics_container.find_elements(By.CSS_SELECTOR, 'li[class*="params-paramsList__item-"]')

            for char_el in char_elements:
                try:
                    name_el = char_el.find_element(By.CSS_SELECTOR, 'span[class*="module-noAccent-"]')
                    name = name_el.text.strip().replace(':', '')

                    full_text = char_el.text.strip()
                    if full_text.startswith(name):
                         value = full_text[len(name):].strip()
                         if value.startswith(':'):
                             value = value[1:].strip()
                    else:
                         value = full_text

                    if name and value:
                         characteristics_dict[name] = value

                except NoSuchElementException: pass
                except Exception as e_char: pass

            apartment_data['original_avito_data']['характеристики'] = characteristics_dict

            apartment_data['max_people'] = parse_numeric_characteristic(characteristics_dict, ['Количество гостей'])
            apartment_data['sleeping_places'] = parse_numeric_characteristic(characteristics_dict, ['Спальные места', 'Количество спальных мест'])

            num_rooms_char = extract_from_characteristics(characteristics_dict, ['Комнат в квартире', 'Количество комнат'])
            if num_rooms_char:
                 if 'студия' in num_rooms_char.lower():
                      apartment_data['sleeping_rooms'] = 0
                 else:
                     apartment_data['sleeping_rooms'] = parse_number(num_rooms_char)
            elif 'количество_комнат' in apartment_data.get('original_avito_data', {}) and apartment_data['original_avito_data']['количество_комнат'] != 'N/A':
                 title_rooms = apartment_data['original_avito_data']['количество_комнат']
                 if 'студия' in title_rooms.lower():
                     apartment_data['sleeping_rooms'] = 0
                 else:
                     apartment_data['sleeping_rooms'] = parse_number(title_rooms)
            else:
                 apartment_data['sleeping_rooms'] = None


            bathroom_char = extract_from_characteristics(characteristics_dict, ['Санузел'])
            if bathroom_char:
                 num_match = re.search(r'\d+', bathroom_char)
                 if num_match:
                      apartment_data['bathrooms'] = parse_number(num_match.group(0))
                 elif 'совмещенный' in bathroom_char.lower() or 'раздельный' in bathroom_char.lower() or 'один' in bathroom_char.lower():
                      apartment_data['bathrooms'] = 1

            apartment_data['square'] = parse_numeric_characteristic(characteristics_dict, ['Общая площадь', 'Площадь'])
            if apartment_data['square'] is None and 'общая_площадь_м2' in apartment_data.get('original_avito_data', {}) and apartment_data['original_avito_data']['общая_площадь_м2'] != 'N/A':
                apartment_data['square'] = parse_number(apartment_data['original_avito_data']['общая_площадь_м2'])


            min_nights_char = extract_from_characteristics(characteristics_dict, ['Минимальный срок аренды', 'Срок аренды'])
            if min_nights_char:
                 num_match = re.search(r'\d+', min_nights_char)
                 if num_match:
                      value = parse_number(num_match.group(0))
                      if 'сутки' in min_nights_char.lower() or 'день' in min_nights_char.lower():
                           apartment_data['min_nights'] = value
                      elif 'месяц' in min_nights_char.lower() and value is not None:
                           apartment_data['min_nights'] = value * 30


            amenity_keys = [
                'Парковка', 'Лифт', 'Балкон', 'Лоджия', 'Окна', 'Вид из окон',
                'В доме', 'Ремонт', 'Техника', 'Мебель', 'Комфорт',
                'Дополнительно'
            ]
            amenities_list = []
            for key in amenity_keys:
                 if key in characteristics_dict and characteristics_dict[key]:
                      amenities_list.append(f"{key}: {characteristics_dict[key]}")

            apartment_data['amenities'] = json.dumps(amenities_list)


        except NoSuchElementException: pass
        except Exception as e:
            pass

        if 'этаж_инфо' in apartment_data.get('original_avito_data', {}) and apartment_data['original_avito_data']['этаж_инфо'] != 'N/A':
            floor_match = re.match(r'(\d+)', apartment_data['original_avito_data']['этаж_инфо'])
            if floor_match:
                apartment_data['stage'] = floor_match.group(1)


        try:
            collected_photo_urls = set()

            try:
                main_image_wrapper = driver.find_element(By.CSS_SELECTOR, '[data-marker="image-frame/image-wrapper"]')
                main_image_url_data = main_image_wrapper.get_attribute('data-url')
                if main_image_url_data:
                     collected_photo_urls.add(main_image_url_data)
            except NoSuchElementException: pass

            try:
                thumbnail_images = driver.find_elements(By.CSS_SELECTOR, 'ul[data-marker="image-preview/preview-wrapper"] li[data-marker="image-preview/item"] img')

                for img_el in thumbnail_images:
                     try:
                          srcset_attr = img_el.get_attribute('srcset')
                          data_src_attr = img_el.get_attribute('data-src')
                          src_attr = img_el.get_attribute('src')

                          best_url = None

                          if srcset_attr:
                               best_url_from_srcset = parse_srcset(srcset_attr)
                               if best_url_from_srcset:
                                   best_url = best_url_from_srcset

                          if not best_url and data_src_attr and not data_src_attr.startswith('data:image'):
                               best_url = data_src_attr

                          if not best_url and src_attr and not src_attr.startswith('data:image'):
                               best_url = src_attr

                          if best_url and not best_url.startswith('data:image'):
                               if best_url.startswith('//'): best_url = 'https:' + best_url
                               elif best_url.startswith('/'): best_url = 'https://www.avito.ru' + best_url

                               collected_photo_urls.add(best_url)

                          elif not best_url:
                               pass

                     except StaleElementReferenceException: pass
                     except Exception as e_img: pass

            except NoSuchElementException: pass

            photo_list = list(collected_photo_urls)
            if photo_list:
                 apartment_data['image_url'] = photo_list[0]

            apartment_data['original_avito_data']['фотографии_детально'] = photo_list


        except NoSuchElementException: pass
        except Exception as e:
            pass


    except TimeoutException:
        pass
    except Exception as e:
        pass


    if 'original_avito_data' in apartment_data and not apartment_data['original_avito_data']:
        del apartment_data['original_avito_data']


    return apartment_data

def save_to_json(data, filename):
    if not data:
        print("Нет данных для сохранения.")
        return

    try:
        with open(filename, 'w', encoding='utf-8') as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=4)
        print("Данные успешно сохранены в файл:", filename)
    except IOError as e:
        print("Ошибка при записи в файл", filename, ":", e)
    except Exception as e:
        print("Непредвиденная ошибка при сохранении в JSON:", e)

if __name__ == "__main__":
    print("--- СКРИПТ ЗАПУЩЕН ---")
    driver = None
    all_collected_data = []
    page_count = 0
    error_occurred = False

    print("### ВНИМАНИЕ: Скрипт настроен на парсинг ВСЕХ объявлений со всех страниц списка.")
    print("### Это может занять много времени и увеличить риск блокировки.")
    print(f"### Если вы хотите ограничить количество, установите MAX_PAGES_TO_PARSE или MAX_APARTMENTS_TO_SCRAPE.")
    print("--- НАЧАЛО БЛОКА TRY ---")

    try:
        driver = setup_driver()
        print("--- Драйвер успешно инициализирован (или попытка инициализации) ---")

        if driver is None:
            print("--- Драйвер НЕ БЫЛ ИНИЦИАЛИЗИРОВАН, ВЫЗЫВАЕМ ИСКЛЮЧЕНИЕ ---")
            raise Exception("Не удалось инициализировать веб-драйвер.")

        print("Загрузка страницы списка:", URL)
        driver.get(URL)
        print("--- Страница загружена ---")

        time.sleep(5)

        while True:
            if MAX_PAGES_TO_PARSE is not None and page_count >= MAX_PAGES_TO_PARSE:
                print("\nДостигнут лимит в", MAX_PAGES_TO_PARSE, "страниц списка. Завершение.")
                break

            page_count += 1
            print("\n=== Обработка страницы списка", page_count, "===")
            print("--- Вызываем scrape_listing_page ---") 
            basic_listings_data = scrape_listing_page(driver)
            print(f"--- scrape_listing_page завершен, найдено {len(basic_listings_data)} базовых записей ---") # <-- И эту

            if basic_listings_data:
                print("Найдено", len(basic_listings_data), "объявлений на странице списка", page_count, ". Обработка деталей...")
                processed_on_this_page_count = 0
                for i, listing in enumerate(basic_listings_data):
                    listing_url = listing.get('ссылка')
                    listing_id = listing.get('id', 'N/A')

                    if listing_url and listing_url != 'N/A':
                         already_detailed = any(d.get('avito_id') == listing_id for d in all_collected_data)

                         if not already_detailed:
                            processed_on_this_page_count += 1
                            print(f"Парсинг детальной страницы {processed_on_this_page_count} с страницы списка {page_count} (Общее обработанных: {len(all_collected_data)+1}) ID: {listing_id} URL: {listing_url}...")
                            print("--- Вызываем scrape_apartment_detail ---") 
                            try:
                                time.sleep(PAUSE_BETWEEN_DETAIL_PAGES)

                                detail_data = scrape_apartment_detail(driver, listing_url)
                                print("--- scrape_apartment_detail успешно завершен ---") # <-- И эту

                                if detail_data['name'] == 'N/A' and 'наименование' in listing and listing['наименование'] != 'N/A':
                                     detail_data['name'] = listing['наименование']
                                if detail_data['square'] is None and 'общая_площадь_м2' in listing and listing['общая_площадь_м2'] != 'N/A':
                                     detail_data['square'] = parse_number(listing['общая_площадь_м2'])
                                if detail_data['sleeping_rooms'] is None and 'количество_комнат' in listing and listing['количество_комнат'] != 'N/A':
                                     title_rooms = listing['количество_комнат']
                                     if 'студия' in title_rooms.lower():
                                          detail_data['sleeping_rooms'] = 0
                                     else:
                                          detail_data['sleeping_rooms'] = parse_number(title_rooms)
                                if detail_data['stage'] is None and 'этаж_инфо' in listing and listing['этаж_инфо'] != 'N/A':
                                     floor_match = re.match(r'(\d+)', listing['этаж_инфо'])
                                     if floor_match:
                                          detail_data['stage'] = floor_match.group(1)

                                if detail_data['image_url'] is None and 'фотографии_список' in listing and listing['фотографии_список']:
                                    if listing['фотографии_список'][0] and listing['фотографии_список'][0] != 'N/A':
                                         detail_data['image_url'] = listing['фотографии_список'][0]

                                for key in ['наименование', 'количество_комнат', 'общая_площадь_м2', 'этаж_инфо', 'фотографии_список']:
                                     if key in listing and key not in detail_data.get('original_avito_data', {}):
                                          if 'original_avito_data' not in detail_data:
                                               detail_data['original_avito_data'] = {}
                                          detail_data['original_avito_data'][key] = listing[key]


                                all_collected_data.append(detail_data)

                            except Exception as e_detail_scrape:
                                 print(f"--- ГЛОБАЛЬНАЯ ОШИБКА ДЕТАЛИ --- Произошла ошибка при обработке детальной страницы для {listing_url} (ID: {listing_id}): {e_detail_scrape}")
                                 error_occurred = True
                                 basic_apartment = {
                                     'avito_id': listing.get('id', 'N/A'),
                                     'avito_link': listing.get('ссылка', 'N/A'),
                                     'name': listing.get('наименование', 'N/A'),
                                     'city': None, 'street': None, 'housenum': None,
                                     'stage': parse_floor_info(listing.get('этаж_инфо', '') if listing.get('этаж_инфо') != 'N/A' else None),
                                     'number': None,
                                     'description': 'N/A',
                                     'max_people': None, 'sleeping_places': None, 'sleeping_rooms': parse_rooms_info(listing.get('количество_комнат', '') if listing.get('количество_комнат') != 'N/A' else None), 'bathrooms': None,
                                     'square': parse_number(listing.get('общая_площадь_м2', '') if listing.get('общая_площадь_м2') != 'N/A' else None),
                                     'cost_per_night': None, 'prepayment': None, 'min_nights': None,
                                     'free_at': None, 'nearby_objects': '[]', 'amenities': '[]', 'living_rules': '[]',
                                     'image_url': listing['фотографии_список'][0] if listing.get('фотографии_список') else None,
                                     'original_avito_data': listing
                                 }
                                 all_collected_data.append(basic_apartment)


                    else:
                        print(f"Пропускаю объявление без ссылки (ID: {listing_id}) с страницы списка {page_count}. Сохраняю базовые данные.")
                        basic_apartment = {
                            'avito_id': listing.get('id', 'N/A'),
                            'avito_link': listing.get('ссылка', 'N/A'),
                            'name': listing.get('наименование', 'N/A'),
                            'city': None, 'street': None, 'housenum': None,
                            'stage': parse_floor_info(listing.get('этаж_инфо', '') if listing.get('этаж_инфо') != 'N/A' else None),
                            'number': None,
                            'description': 'N/A',
                            'max_people': None, 'sleeping_places': None, 'sleeping_rooms': parse_rooms_info(listing.get('количество_комнат', '') if listing.get('количество_комнат') != 'N/A' else None), 'bathrooms': None,
                            'square': parse_number(listing.get('общая_площадь_м2', '') if listing.get('общая_площадь_м2') != 'N/A' else None),
                            'cost_per_night': None, 'prepayment': None, 'min_nights': None,
                            'free_at': None, 'nearby_objects': '[]', 'amenities': '[]', 'living_rules': '[]',
                            'image_url': listing['фотографии_список'][0] if listing.get('фотографии_список') else None,
                            'original_avito_data': listing
                        }
                        all_collected_data.append(basic_apartment)

            else:
                print(f"На странице списка {page_count} не было собрано базовых записей для детального парсинга.")

            try:
                next_button_selector = 'a[data-marker="pagination-button/nextPage"]'
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)

                next_button = WebDriverWait(driver, 10).until(
                     EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
                 )
                print("Найдена кнопка 'Следующая страница'. Переход...")
                next_page_url = next_button.get_attribute('href')
                driver.get(next_page_url)
                print("--- Перешли на следующую страницу списка ---") 
                time.sleep(7)

            except (NoSuchElementException, TimeoutException):
                print("\nКнопка 'Следующая страница' не найдена или не активна. Завершение парсинга пагинации.")
                break
            except Exception as e_inner:
                print(f"Ошибка при переходе на следующую страницу списка: {e_inner}")
                error_occurred = True
                break

    except Exception as e_global:
        print(f"Произошла глобальная ошибка во время выполнения: {e_global}")
        error_occurred = True
    finally:
        print("--- Блок finally начал выполнение ---") 
        if driver:
            print("Закрытие браузера...")
            driver.quit()
            print("--- Браузер закрыт ---") # <-- И эту

    print("--- Блок после try/except/finally начал выполнение ---") 
    if all_collected_data:
         print("\nВсего собрано", len(all_collected_data), "уникальных объявлений (базовые + детальные данные).")
         cleaned_data = []
         for item in all_collected_data:
              if 'original_avito_data' in item and not item['original_avito_data']:
                   temp_item = item.copy()
                   del temp_item['original_avito_data']
                   cleaned_data.append(temp_item)
              else:
                   cleaned_data.append(item)

         save_to_json(cleaned_data, OUTPUT_JSON_FILE)

         if error_occurred:
             print("Примечание: Сохранение произведено, но во время работы скрипта возникли ошибки при парсинге.")
    else:
         if error_occurred:
             print("\nНе было собрано данных из-за возникшей глобальной ошибки.")
         else:
             print("\nНе было собрано ни одного объявления. Проверьте URL или селекторы.")
    print("--- СКРИПТ ЗАВЕРШЕН (нормальное завершение) ---") 