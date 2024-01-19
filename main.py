from data_handler import export_to_csv
from scraping import CategoryScraping, get_all_categories


def export_category(category: dict) -> bool:
    category_scraping = CategoryScraping(route=category['url'], category_name=category['title'])
    category_books = category_scraping.get_books()
    print(f"[INFO] Creating CSV file...")
    status = export_to_csv(data=category_books, csv_file=category['title'] + '.csv')
    if status:
        print('[OK] Export finished with success')
        return True
    else:
        print('[ERROR] Export has failed')
        return False


def main():
    success = True
    print("[INFO] Web Scraping in progress...")
    categories = get_all_categories()
    for category in categories:
        status = export_category(category)
        if not status:
            success = False

    return success


if __name__ == '__main__':
    scraping_status = main()
    if scraping_status:
        print('[OK] Web Scraping finished')
    else:
        print('[ERROR] Process failed')
