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

# --- Настройки ---
# URL страницы списка квартир
URL = "https://www.avito.ru/moskva/kvartiry/sdam"
# Имя выходного JSON файла
OUTPUT_JSON_FILE = 'avito_apartments_sdam_all_optimized.json'  # Изменил имя файла
# Сколько секунд ждать загрузки основных элементов страницы
WAIT_TIMEOUT_LIST = 15 # Таймаут для страницы списка
WAIT_TIMEOUT_DETAIL = 20 # Таймаут для страницы объявления

# Сколько страниц списка парсить (None - все доступные)
MAX_PAGES_TO_PARSE = None # Установите None для парсинга всех страниц

# *** ОГРАНИЧЕНИЕ НА КОЛИЧЕСТВО ОБЪЯВЛЕНИЙ СНЯТО ***
MAX_APARTMENTS_TO_SCRAPE = None # Установлено None

# Настройки для плавной прокрутки и парсинга списка
SCROLL_PAUSE_TIME = 1.5 # Немного уменьшил паузу после прокрутки списка
SCROLL_INCREMENT_RATIO = 0.8 # Прокручивать на 80% высоты окна списка
SCROLL_TOLERANCE = 10 # Допустимое отклонение в пикселях при проверке конца страницы списка
PAUSE_AFTER_NEW_ITEM_FOUND_LIST = 0.5 # Немного уменьшил паузу после обнаружения НОВОГО элемента в списке

# Настройки для парсинга страниц объявлений
# PAUSE_BEFORE_DETAIL_SCRAPE = 2.0 # Эту паузу заменяем на WebDriverWait
PAUSE_BETWEEN_DETAIL_PAGES = 1.5 # Немного уменьшил паузу между посещениями страниц объявлений

# --- Функции ---

def setup_driver():
    """Настраивает и возвращает экземпляр веб-драйвера Chrome."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Раскомментируйте для запуска без окна браузера
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
    """Извлекает информацию об этаже из строки заголовка."""
    match = re.search(r'(\d+)/(\d+)\s+эт', title_text)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return "N/A"

def parse_rooms_info(title_text):
    """Извлекает информацию о количестве комнат из строки заголовка."""
    room_match = re.search(r'(\d+)-к', title_text)
    if room_match:
        return room_match.group(1)
    if "студия" in title_text.lower():
         return "Студия"
    if "комната" in title_text.lower():
         return "Комната"
    return "N/A"

def parse_area_info(title_text):
    """Извлекает информацию об общей площади из строки заголовка."""
    match = re.search(r'(\d+[\,\.]?\d*)\s*м²', title_text)
    if match:
        return match.group(1).replace(',', '.')
    return "N/A"


def scrape_listing_page(driver):
    """
    Парсит основные данные с текущей открытой страницы СПИСКА,
    постепенно прокручивая ее и собирая данные по мере появления новых объявлений.
    Возвращает список словарей с базовой информацией (включая URL объявления).
    """
    all_page_data = []
    processed_item_ids = set() # Используем множество для отслеживания уже добавленных ID в all_page_data для этой страницы

    print("Начинаю прокрутку и парсинг страницы списка объявлений...")

    time.sleep(3)

    try:
        items_container_selector = 'div[data-marker="catalog-serp"]'
        WebDriverWait(driver, WAIT_TIMEOUT_LIST).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, items_container_selector))
        )
        print("Основной контейнер объявлений списка загружен.")

        last_scroll_position = -1
        scroll_attempts = 0

        while True: # Цикл прокрутки по текущей странице списка
            scroll_attempts += 1
            try:
                # Убедимся, что хотя бы один элемент item присутствует после прокрутки
                WebDriverWait(driver, 5).until(
                     EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="item"]'))
                )
                listing_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-marker="item"]')
            except (TimeoutException, StaleElementReferenceException):
                 print(f"Шаг {scroll_attempts}: Не удалось найти элементы 'item' на странице списка или ссылки устарели.")
                 listing_elements = []


            current_items_on_page_count = len(listing_elements)
            new_items_found_in_scroll = 0
            parsed_in_this_scroll = [] # Временно храним данные для элементов, найденных в эту итерацию прокрутки

            current_scroll_items_to_process = []
            for item in listing_elements:
                 try:
                     item_id = item.get_attribute('data-item-id')
                     # Проверяем, что ID не None/пустой И еще не обработан в этом вызове scrape_listing_page
                     if item_id and item_id not in processed_item_ids:
                          current_scroll_items_to_process.append((item_id, item))
                          processed_item_ids.add(item_id) # Сразу помечаем как обрабатываемый
                 except StaleElementReferenceException:
                      pass # Элемент устарел, пропускаем его в этой итерации
                 except Exception as e:
                     #print(f"Ошибка при первичном получении ID элемента списка: {e}")
                     pass

            new_items_found_in_scroll = len(current_scroll_items_to_process)
            if new_items_found_in_scroll > 0:
                 print(f"Шаг прокрутки списка {scroll_attempts}: Обнаружено {new_items_found_in_scroll} новых объявлений.")


            for item_id, item in current_scroll_items_to_process:
                    # Пауза после обнаружения нового элемента перед парсингом его базовых данных
                    time.sleep(PAUSE_AFTER_NEW_ITEM_FOUND_LIST)

                    data = {
                        'id': item_id,
                        'наименование': 'N/A',
                        'количество_комнат': 'N/A',
                        'общая_площадь_м2': 'N/A',
                        'этаж_инфо': 'N/A',
                        'ссылка': 'N/A', # Ссылка важна для детального парсинга
                        'фотографии_список': [] # Фото с страницы списка
                    }

                    # Извлечение данных из элемента списка
                    try:
                        title_element = item.find_element(By.CSS_SELECTOR, 'a[data-marker="item-title"]')
                        raw_title = title_element.text.strip()
                        data['наименование'] = raw_title
                        data['ссылка'] = title_element.get_attribute('href')
                        data['количество_комнат'] = parse_rooms_info(raw_title)
                        data['этаж_инфо'] = parse_floor_info(raw_title)
                        data['общая_площадь_м2'] = parse_area_info(raw_title)
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                         # print(f"--- Отладка списка --- Не удалось получить основные данные для ID {item_id}: {e}")
                         pass

                    # Фотографии с страницы списка (превью)
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
                        # print(f"--- Отладка списка --- Не удалось получить фото для ID {item_id}: {e}")
                        pass


                    # Добавляем базовые данные в список
                    parsed_in_this_scroll.append(data)


            if parsed_in_this_scroll: # Добавляем собранные в этой итерации данные
                 all_page_data.extend(parsed_in_this_scroll)


            # --- Логика прокрутки и проверки условия выхода из цикла прокрутки страницы списка ---
            current_scroll_position = driver.execute_script("return window.pageYOffset;")
            viewport_height = driver.execute_script("return window.innerHeight;")
            document_height = driver.execute_script("return document.body.scrollHeight;")

            scroll_by = int(viewport_height * SCROLL_INCREMENT_RATIO)
            if current_scroll_position + viewport_height + scroll_by >= document_height:
                 scroll_by = document_height - (current_scroll_position + viewport_height) + 50
                 if scroll_by <= 0:
                     scroll_by = 0 # Уже внизу

            driver.execute_script(f"window.scrollBy(0, {scroll_by});")

            time.sleep(SCROLL_PAUSE_TIME)

            new_scroll_position = driver.execute_script("return window.pageYOffset;")
            new_document_height = driver.execute_script("return document.body.scrollHeight;")

            try:
                # Пересчитываем общее количество элементов после прокрутки
                updated_listing_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-marker="item"]')
                updated_items_count = len(updated_listing_elements)
            except StaleElementReferenceException:
                 # Если элементы устарели, предполагаем, что новых нет в этой итерации
                 updated_items_count = current_items_on_page_count


            item_count_not_increasing = updated_items_count <= current_items_on_page_count
            scroll_position_not_changing = abs(new_scroll_position - last_scroll_position) < SCROLL_TOLERANCE


            # Условие выхода из цикла прокрутки текущей страницы списка
            # Выходим, если новых элементов не найдено ИЛИ (позиция скролла не меняется И количество элементов не растет)
            if new_items_found_in_scroll == 0 or (scroll_position_not_changing and item_count_not_increasing):
                 print("\nЗавершение прокрутки страницы списка: Новые объявления не появляются или достигнут конец.")
                 break

            # Дополнительная проверка на застревание
            at_very_bottom = (current_scroll_position + viewport_height) >= document_height - SCROLL_TOLERANCE - 50
            if new_items_found_in_scroll > 0 and scroll_position_not_changing and not at_very_bottom:
                 print("\nВнимание: Найдены новые объявления, но позиция прокрутки списка не меняется. Завершение прокрутки.")
                 break


            last_scroll_position = new_scroll_position


    except TimeoutException:
        print("Время ожидания загрузки основного контейнера списка истекло.")
    except Exception as e:
        print(f"Произошла ошибка при парсинге страницы списка: {e}")

    print(f"Парсинг страницы списка завершен. Собрано {len(all_page_data)} уникальных базовых записей с этой страницы.")
    return all_page_data


def scrape_apartment_detail(driver, listing_url):
    """
    Переходит на страницу конкретного объявления и парсит подробную информацию.
    Возвращает словарь с детальными данными.
    """
    detail_data = {
        'цена': 'N/A',
        'залог': 'N/A',
        'комиссия': 'N/A',
        'адрес': 'N/A',
        'метро': 'N/A',
        'описание_полное': 'N/A',
        'дата_публикации_детально': 'N/A',
        'характеристики': {},
        'фотографии_детально': []
    }

    # print(f"\nПерехожу на страницу объявления: {listing_url}")


    try:
        driver.get(listing_url)
        # Ожидаем появления элемента цены как индикатора загрузки ключевых данных
        # Используем более надежный селектор, который включает data-marker
        WebDriverWait(driver, WAIT_TIMEOUT_DETAIL).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="item-view/item-price"]'))
        )
        # Убираем фиксированную паузу, полагаясь на WebDriverWait
        # time.sleep(PAUSE_BEFORE_DETAIL_SCRAPE)


        # --- Парсинг детальных данных ---
        # Селекторы обновлены на основе предоставленного HTML

        # Цена (попытка извлечь из content атрибута, затем из текста)
        try:
            # Сначала пробуем content атрибут с элемента с data-marker
            price_element_for_attr = driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-price"]')
            price_value = price_element_for_attr.get_attribute('content')

            if price_value:
                 detail_data['цена'] = price_value.strip()
                 # print(f"--- Отладка детали --- Получена ЦЕНА из content атрибута: {detail_data['цена']} ({listing_url})")
            else:
                 # Если content атрибут пустой или нет, пробуем получить текст с родительского элемента (который включает "в месяц")
                 try:
                      price_element_for_text = driver.find_element(By.CSS_SELECTOR, '#bx_item-price-value')
                      detail_data['цена'] = price_element_for_text.text.strip()
                      # print(f"--- Отладка детали --- Получена ЦЕНА из текста элемента #bx_item-price-value: {detail_data['цена']} ({listing_url})")
                 except NoSuchElementException:
                      # Если #bx_item-price-value не найден, пробуем текст с элемента data-marker (только число и ₽)
                      try:
                           price_element_alt_text = driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-price"]')
                           detail_data['цена'] = price_element_alt_text.text.strip() + " (только число+₽)"
                           # print(f"--- Отладка детали --- Получена ЦЕНА из текста элемента data-marker: {detail_data['цена']} ({listing_url})")
                      except NoSuchElementException:
                           print(f"--- Отладка детали --- Элементы цены не найдены ни по одному селектору ({listing_url}).")
                 except Exception as e_text:
                       print(f"--- Отладка детали --- Ошибка при получении текста ЦЕНЫ ({listing_url}): {e_text}")


            if not detail_data['цена'] or detail_data['цена'] == 'N/A':
                 # Если после всех попыток цена все еще N/A
                 print(f"--- Отладка детали --- Элемент(ы) цены найдены, но значение (content или text) не удалось получить ({listing_url}).")


        except (NoSuchElementException, StaleElementReferenceException) as e:
            # Если элемент data-marker="item-view/item-price" не найден вообще
            print(f"--- Отладка детали --- Не удалось найти элемент data-marker=\"item-view/item-price\" для парсинга цены ({listing_url}): {e}")
            pass
        except Exception as e:
            print(f"--- Отладка детали --- Непредвиденная ошибка при парсинге ЦЕНЫ ({listing_url}): {e}")
            pass

        # Залог и Комиссия
        try:
             # Ищем span, содержащий текст залога и комиссии
             deposit_fee_element = driver.find_element(By.CSS_SELECTOR, '.styles-item-price-sub-price-A1IZy span')
             deposit_fee_text = deposit_fee_element.text.strip()

             # Парсим текст для извлечения залога и комиссии
             # Ищем число (включая пробелы в качестве разделителя тысяч) перед '₽' после слова 'залог'
             deposit_match = re.search(r'залог\s*([\d\s]+)\s*₽', deposit_fee_text)
             if deposit_match:
                  detail_data['залог'] = deposit_match.group(1).replace('\xa0', '').replace(' ', '').strip() # Удаляем неразрывные и обычные пробелы

             # Ищем число (включая пробелы в качестве разделителя тысяч) перед '₽' после слова 'комиссия'
             fee_match = re.search(r'комиссия\s*([\d\s]+)\s*₽', deposit_fee_text)
             if fee_match:
                  detail_data['комиссия'] = fee_match.group(1).replace('\xa0', '').replace(' ', '').strip() # Удаляем неразрывные и обычные пробелы

             if detail_data['залог'] == 'N/A' and detail_data['комиссия'] == 'N/A' and deposit_fee_text:
                  # Если элемент найден, но парсинг не удался
                  print(f"--- Отладка детали --- Элемент залога/комиссии найден, но не удалось распарсить значения из текста: '{deposit_fee_text}' ({listing_url})")


        except (NoSuchElementException, StaleElementReferenceException) as e:
            # Если элемент залога/комиссии не найден
            # print(f"--- Отладка детали --- Не удалось найти элемент залога/комиссии по селектору '.styles-item-price-sub-price-A1IZy span' ({listing_url}): {e}")
            pass # Не всегда есть залог/комиссия, поэтому не печатаем ошибку, если элемент просто отсутствует
        except Exception as e:
            print(f"--- Отладка детали --- Ошибка при парсинге залога/комиссии ({listing_url}): {e}")
            pass


        # Адрес
        try:
            # Используем новый селектор для адреса
            address_element = driver.find_element(By.CSS_SELECTOR, '[itemprop="address"] .style-item-address__string-wt61A')
            detail_data['адрес'] = address_element.text.strip()
        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(f"--- Отладка детали --- Не удалось получить АДРЕС ({listing_url}): {e}")
            pass
        except Exception as e:
            print(f"--- Отладка детали --- Ошибка при парсинге АДРЕСА ({listing_url}): {e}")
            pass

        # Метро и удаленность
        try:
            # Используем новый селектор для метро
            metro_elements = driver.find_elements(By.CSS_SELECTOR, '[itemprop="address"] .style-item-address-georeferences-item-TZsrp')
            metro_info = [el.text.strip() for el in metro_elements if el.text.strip()]
            detail_data['метро'] = ", ".join(metro_info) if metro_info else "N/A"
            if not metro_info and metro_elements: # Если элементы найдены, но текст пустой
                 print(f"--- Отладка детали --- Элемент(ы) МЕТРО найдены, но текст пустой или состоит из пробелов ({listing_url}).")
        except (NoSuchElementException, StaleElementReferenceException) as e:
            # print(f"--- Отладка детали --- Не удалось найти элемент МЕТРО ({listing_url}): {e}")
            pass # Не всегда есть метро, поэтому не печатаем ошибку, если элемент просто отсутствует
        except Exception as e:
            print(f"--- Отладка детали --- Ошибка при парсинге МЕТРО ({listing_url}): {e}")
            pass

        # Полное описание (селектор остался прежним, т.к. он сработал)
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, '[itemprop="description"]')
            detail_data['описание_полное'] = description_element.text.strip()
        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(f"--- Отладка детали --- Не удалось получить ПОЛНОЕ ОПИСАНИЕ ({listing_url}): {e}")
            pass
        except Exception as e:
            print(f"--- Отладка детали --- Ошибка при парсинге ПОЛНОГО ОПИСАНИЯ ({listing_url}): {e}")
            pass

        # Дата публикации (детально)
        try:
             # Используем новый селектор data-marker для даты
             date_element = driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-date"]')
             detail_data['дата_публикации_детально'] = date_element.text.strip()
        except (NoSuchElementException, StaleElementReferenceException) as e:
             print(f"--- Отладка детали --- Не удалось найти элемент ДАТЫ ПУБЛИКАЦИИ ({listing_url}): {e}")
             pass
        except Exception as e:
            print(f"--- Отладка детали --- Ошибка при парсинге ДАТЫ ПУБЛИКАЦИИ ({listing_url}): {e}")
            pass


        # Характеристики
        try:
            # Селектор контейнера остался прежним
            characteristics_container = driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-params"]')
            # Селектор строк характеристик обновлен с использованием части класса
            char_elements = characteristics_container.find_elements(By.CSS_SELECTOR, 'li[class*="params-paramsList__item-"]')

            if not char_elements and characteristics_container: # Проверяем, если контейнер есть, но строк нет
                 print(f"--- Отладка детали --- Контейнер характеристик найден, но нет строк характеристик по селектору 'li[class*=\"params-paramsList__item-\"]' ({listing_url}).")

            for i, char_el in enumerate(char_elements):
                try:
                    # Селектор названия характеристики обновлен
                    name_el = char_el.find_element(By.CSS_SELECTOR, 'span[class*="module-noAccent-"]')
                    name = name_el.text.strip().replace(':', '')

                    # Логика извлечения значения: берем весь текст строки и удаляем текст названия
                    full_text = char_el.text.strip()
                    if full_text.startswith(name):
                         value = full_text[len(name):].strip()
                         # Дополнительно удаляем двоеточие и пробелы, если они остались в начале значения
                         if value.startswith(':'):
                             value = value[1:].strip()
                    else:
                         # Если текст строки не начинается с названия, возможно, структура другая
                         value = full_text # Сохраняем весь текст строки как значение
                         # print(f"--- Отладка детали --- Необычная структура строки характеристики ({listing_url}, элемент {i+1}): '{full_text}'")


                    if name and value:
                         detail_data['характеристики'][name] = value
                    # elif name: # Отладочная печать для характеристики без значения
                         # print(f"--- Отладка детали --- Найдена характеристика '{name}', но значение пустое ({listing_url}, элемент {i+1}).")


                except NoSuchElementException:
                     print(f"--- Отладка детали --- Не удалось найти элементы названия/значения характеристики в строке {i+1} ({listing_url}). Возможно, селектор 'span[class*=\"module-noAccent-\"]' некорректен.")
                     pass
                except Exception as e_char:
                     print(f"--- Отладка детали --- Ошибка при парсинге строки характеристики {i+1} ({listing_url}): {e_char}")
                     pass

            if not detail_data['характеристики'] and characteristics_container: # Если контейнер есть, но словарь пуст
                 print(f"--- Отладка детали --- Словарь характеристик остался пустым, хотя контейнер найден ({listing_url}). Проверьте селекторы строк и элементов внутри.")

        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(f"--- Отладка детали --- Не найден контейнер характеристик по селектору '[data-marker=\"item-view/item-params\"]' ({listing_url}): {e}")
            pass
        except Exception as e:
            print(f"--- Отладка детали --- Ошибка при парсинге блока характеристик ({listing_url}): {e}")
            pass


        # Фотографии с детальной страницы
        try:
            # Попытка получить URL из data-url главного контейнера изображения
            # Используем новый селектор для контейнера главного изображения
            main_image_wrapper = driver.find_element(By.CSS_SELECTOR, '[data-marker="image-frame/image-wrapper"]')
            main_image_url = main_image_wrapper.get_attribute('data-url')
            if main_image_url and main_image_url not in detail_data['фотографии_детально']:
                 detail_data['фотографии_детально'].append(main_image_url)
                 # print(f"--- Отладка детали --- Добавлено главное фото из data-url ({listing_url}).")
            else:
                 # Если data-url пустой или нет, пробуем найти img внутри (как запасной вариант)
                 try:
                      img_el = main_image_wrapper.find_element(By.TAG_NAME, 'img')
                      src = img_el.get_attribute('data-src') or img_el.get_attribute('src')
                      if src and not src.startswith('data:image'):
                           if src.startswith('//'): src = 'https:' + src
                           elif src.startswith('/'): src = 'https://www.avito.ru' + src
                           if src and src not in detail_data['фотографии_детально']:
                                detail_data['фотографии_детально'].append(src)
                 except NoSuchElementException:
                      print(f"--- Отладка детали --- Найден контейнер главного изображения, но нет img внутри ({listing_url}).")


            # Попытка получить URLы из превью-миниатюр
            # Используем новый селектор для миниатюр
            thumbnail_images = driver.find_elements(By.CSS_SELECTOR, 'ul[data-marker="image-preview/preview-wrapper"] li[data-marker="image-preview/item"] img')

            if not thumbnail_images and not detail_data['фотографии_детально']: # Если не нашли главное фото и нет миниатюр
                 print(f"--- Отладка детали --- Не найдено ни одного элемента img в галерее (главное фото и миниатюры) по основным селекторам ({listing_url}).")

            for i, img_el in enumerate(thumbnail_images):
                 try:
                      src = img_el.get_attribute('data-src') or img_el.get_attribute('src')
                      if src and not src.startswith('data:image'):
                           if src.startswith('//'): src = 'https:' + src
                           elif src.startswith('/'): src = 'https://www.avito.ru' + src

                           if src and src not in detail_data['фотографии_детально']:
                                detail_data['фотографии_детально'].append(src)
                 except StaleElementReferenceException:
                      print(f"--- Отладка детали --- StaleElementReferenceException при парсинге фото {i+1} ({listing_url}).")
                      pass
                 except Exception as e_img:
                      print(f"--- Отладка детали --- Ошибка при извлечении src/data-src для фото {i+1} ({listing_url}): {e_img}")
                      pass

            if not detail_data['фотографии_детально'] and (main_image_url or thumbnail_images): # Если элементы найдены, но список фото пуст
                 print(f"--- Отладка детали --- Список фотографий детально остался пустым, но элементы img найдены ({listing_url}). Возможно, проблема с src/data-src или base64.")


        except (NoSuchElementException, StaleElementReferenceException) as e:
             print(f"--- Отладка детали --- Не удалось найти контейнер или элементы галереи фото ({listing_url}): {e}")
             pass
        except Exception as e:
            print(f"--- Отладка детали --- Ошибка при парсинге блока фото ({listing_url}): {e}")
            pass


    except TimeoutException:
        print(f"--- Отладка детали --- Время ожидания загрузки страницы объявления истекло ({listing_url}).")
    except Exception as e:
        print(f"--- Отладка детали --- Произошла непредвиденная ошибка при обработке страницы {listing_url}: {e}")


    # print(f"Закончил парсинг объявления: {listing_url}") # Убрал для уменьшения вывода
    return detail_data


# --- Функция для сохранения в JSON ---
def save_to_json(data, filename):
    """Сохраняет собранные данные в JSON файл."""
    if not data:
        print("Нет данных для сохранения.")
        return

    try:
        with open(filename, 'w', encoding='utf-8') as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=4)
        print(f"Данные успешно сохранены в файл: {filename}")
    except IOError as e:
        print(f"Ошибка при записи в файл {filename}: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка при сохранении в JSON: {e}")


# --- Основной блок исполнения скрипта ---
if __name__ == "__main__":
    driver = None
    all_collected_data = [] # Список для хранения всех данных (список + детали)
    page_count = 0 # Счетчик страниц списка
    error_occurred = False

    print("### ВНИМАНИЕ: Скрипт настроен на парсинг ВСЕХ объявлений со всех страниц списка.")
    print("### Это может занять много времени и увеличить риск блокировки.")
    print(f"### Если вы хотите ограничить количество, установите MAX_PAGES_TO_PARSE или MAX_APARTMENTS_TO_SCRAPE.")


    try:
        driver = setup_driver()
        if driver is None:
            raise Exception("Не удалось инициализировать веб-драйвер.")


        print(f"Загрузка страницы списка: {URL}")
        driver.get(URL)
        time.sleep(5)


        # Цикл для обхода страниц пагинации списка
        while True:
            # Ограничение по общему количеству квартир снято, проверка убрана.
            # Ограничение по страницам списка (если задано)
            if MAX_PAGES_TO_PARSE is not None and page_count >= MAX_PAGES_TO_PARSE:
                print(f"\nДостигнут лимит в {MAX_PAGES_TO_PARSE} страниц списка. Завершение.")
                break


            page_count += 1
            print(f"\n=== Обработка страницы списка {page_count} ===")

            # Парсим основные данные со страницы списка
            basic_listings_data = scrape_listing_page(driver)

            if basic_listings_data:
                print(f"Найдено {len(basic_listings_data)} объявлений на странице списка {page_count}.")
                print(f"Текущее общее количество собранных квартир: {len(all_collected_data)}") # Сообщаем текущее общее количество

                # --- Цикл для перехода на страницы объявлений и парсинга деталей ---
                processed_on_this_page_count = 0
                for i, listing in enumerate(basic_listings_data):
                    # Ограничение по общему количеству квартир снято, проверка убрана.

                    listing_url = listing.get('ссылка')
                    listing_id = listing.get('id', 'N/A')

                    if listing_url and listing_url != 'N/A':
                        # Проверяем, не парсили ли мы уже детальную страницу этого объявления (по ID)
                        # Улучшенная проверка на наличие хотя бы одного из полей, которые парсятся только на детализации
                        already_detailed = any(
                            d.get('id') == listing_id and
                            any(key not in ['id', 'ссылка', 'фотографии_список', 'наименование', 'количество_комнат', 'общая_площадь_м2', 'этаж_инфо'] and value not in ('N/A', {}, []) for key, value in d.items())
                            for d in all_collected_data
                        )


                        if not already_detailed:
                            processed_on_this_page_count += 1
                            # Убрал индикатор прогресса относительно лимита, т.к. лимит снят
                            print(f"Парсинг детальной страницы {processed_on_this_page_count} с страницы списка {page_count} (Общее обработанных: {len(all_collected_data)+1}) ID: {listing_id} URL: {listing_url}...")
                            try:
                                time.sleep(PAUSE_BETWEEN_DETAIL_PAGES) # Пауза перед переходом

                                detail_data = scrape_apartment_detail(driver, listing_url)
                                merged_data = {**listing, **detail_data}
                                all_collected_data.append(merged_data)

                            except Exception as e_detail_scrape:
                                 print(f"--- ГЛОБАЛЬНАЯ ОШИБКА ДЕТАЛИ --- Произошла ошибка при обработке детальной страницы для {listing_url} (ID: {listing_id}): {e_detail_scrape}")
                                 all_collected_data.append(listing) # Сохраняем только базовые данные
                                 error_occurred = True
                        # else:
                             # print(f"Объявление ID {listing_id} уже было детализировано, пропускаю.")


                    else:
                        print(f"Пропускаю объявление без ссылки (ID: {listing_id}) с страницы списка {page_count}. Сохраняю базовые данные.")
                        all_collected_data.append(listing)

                # Ограничение по общему количеству квартир снято, проверка убрана.

            else:
                print(f"На странице списка {page_count} не было собрано базовых записей для детального парсинга.")


            # Проверка лимита страниц списка (если задано) уже в начале цикла

            # Поиск кнопки "Следующая страница" и переход
            try:
                next_button_selector = 'a[data-marker="pagination-button/nextPage"]'
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)

                print(f"Поиск кнопки 'Следующая страница' на странице списка {page_count}...")
                next_button = WebDriverWait(driver, 10).until(
                     EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
                 )
                print("Найдена кнопка 'Следующая страница'. Переход...")
                next_page_url = next_button.get_attribute('href')
                driver.get(next_page_url)
                time.sleep(7) # Пауза после перехода на следующую страницу списка

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
        if driver:
            print("Закрытие браузера...")
            driver.quit()

    # --- Финальное сохранение данных ---
    if all_collected_data:
         print(f"\nВсего собрано {len(all_collected_data)} уникальных объявлений (базовые + детальные данные).")
         save_to_json(all_collected_data, OUTPUT_JSON_FILE)

         if error_occurred:
             print("Примечание: Сохранение произведено, но во время работы скрипта возникли ошибки при парсинге.")
    else:
         if error_occurred:
             print("\nНе было собрано данных из-за возникшей глобальной ошибки.")
         else:
             print("\nНе было собрано ни одного объявления. Проверьте URL или селекторы.")