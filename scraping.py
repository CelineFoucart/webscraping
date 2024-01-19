import time

import requests
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com"


class ProductScraping:
    def __init__(self, route: str, category_name: str):
        """Constructor for ProductScraping"""
        self.category_name = category_name
        self.route = route
        self.product = self._set_empty_product()

    def retrieve_product(self) -> bool:
        response = requests.get(self.route)
        if response.ok:
            self._extract_data(response)
            return True
        return False

    def _extract_data(self, response):
        soup = BeautifulSoup(response.text, features="html.parser")
        self.product['title'] = soup.find('h1').text
        keys = ['upc', 'type', 'price_excluding_tax', 'price_including_tax', 'tax', 'number_available',
                'review_rating']
        description = soup.select('#product_description + p ')
        if description:
            self.product['product_description'] = description[0].text
        trim_url = soup.find('img')['src'].lstrip('../')
        self.product['image_url'] = URL + '/' + trim_url
        tds = soup.select('td')
        for index, td in enumerate(tds):
            if keys[index] in self.product:
                self.product[keys[index]] = td.text
        self.product['price_including_tax'] = self.product.get('price_including_tax', '').lstrip('Â£')
        self.product['price_excluding_tax'] = self.product.get('price_excluding_tax', '').lstrip('Â£')
        self.product['review_rating'] = self.product.get('review_rating', '0')

    def _set_empty_product(self):
        product = {
            'upc': '',
            'product_page_url': self.route,
            'title': '',
            'price_including_tax': '',
            'price_excluding_tax': '',
            'number_available': '',
            'product_description': '',
            'category': self.category_name,
            'review_rating': '',
            'image_url': ''
        }
        return product


class CategoryScraping:
    def __init__(self, route: str, category_name: str):
        """Constructor for CategoryScraping"""
        self.category_name = category_name
        self.route = URL + '/' + route
        self.links = []

    def get_books(self) -> list[dict]:
        print(f"[INFO] Scraping category {self.category_name}...")
        status = self._retrieve_all_books()
        if not status:
            print(f"[ERROR] Scraping category {self.category_name} failed")

        elements = []
        for books_link in self.links:
            print(f"[INFO] Scraping book {URL + books_link}")
            product_scraping = ProductScraping(route=URL + books_link, category_name=self.category_name)

            is_success = product_scraping.retrieve_product()
            if is_success:
                elements.append(product_scraping.product)
                print(f"[OK] Scraping book finished with success")
            else:
                print(f"[ERROR] Scraping book failed")
            time.sleep(1)

        return elements

    def _retrieve_all_books(self):
        response = requests.get(self.route)
        if not response.ok:
            return False

        soup = BeautifulSoup(response.text, features="html.parser")
        self._fetch_links(soup)
        self._fetch_next_pages(soup)
        return True

    def _fetch_next_pages(self, soup) -> bool:
        next_page = soup.select('.pager')
        if next_page:
            pagination = next_page[0].select('.current')[0].text
            last_page = int(pagination.split()[-1])

            for i in range(2, last_page + 1):
                response = requests.get(f"{self.route}/page-{i}.html")

                if response.ok:
                    self._fetch_links(BeautifulSoup(response.text, features="html.parser"))
            return True
        return False

    def _fetch_links(self, soup):
        products_links = soup.select('.product_pod h3 a')
        for product_link in products_links:
            href = product_link['href']
            self.links.append('/catalogue/' + href.lstrip('../'))


def get_all_categories() -> list[dict]:
    """
    Retrieve all categories from the home page with a url and a title
    :return: a list of categories, empty in case of error
    """

    categories = []

    response = requests.get(URL+'/index.html')
    if not response.ok:
        return categories

    soup = BeautifulSoup(response.text, features="html.parser")
    categories_links = soup.select('.side_categories ul li ul li a')

    for category_link in categories_links:
        categories.append({
            'title': category_link.string.strip("\n "),
            'url': '/' + category_link['href']
        })

    return categories
