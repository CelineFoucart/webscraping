import csv
import os
import time

import requests

CURRENT_DIR = os.getcwd()
DATA_DIR = os.path.join(CURRENT_DIR, 'data')
IMAGE_DIR = os.path.join(CURRENT_DIR, 'images')


def download_cover(title: str, file_path: str) -> bool:
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    time.sleep(1)

    res = requests.get(file_path, stream=True)
    file_name, file_extension = os.path.splitext(file_path)

    file_extension = file_extension if file_extension else '.jpg'
    invalid_characters = [
        '.', ':', '!', '?', ',', '/', ';', '\n', '&', '*', "#", "%", '@', "'",
        '\\', '`', '|', '"', '{', '}', '<', '>', '$', '+'
    ]

    for letter in invalid_characters:
        title = title.replace(letter, '')
    title = title.replace(' ', '-')
    title = title.lower()

    if res.status_code == 200:
        img_data = res.content
        local_file = f"{title}{file_extension}"

        with open(os.path.join(IMAGE_DIR, local_file), 'wb') as handler:
            handler.write(img_data)
            print(f"[OK] Cover for '{title}' download successfully")
            return True
    return False


def export_to_csv(data: list[dict], csv_file='products.csv') -> bool:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    data_file = os.path.join(DATA_DIR, csv_file)

    csv_columns = [
        'upc',
        'product_page_url',
        'title',
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'product_description',
        'category',
        'review_rating',
        'image_url'
    ]

    try:
        with open(data_file, "w", encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()

            for element in data:
                writer.writerow(element)
                download_cover(title=element['title'], file_path=element['image_url'])

        return True
    except IOError:
        return False

