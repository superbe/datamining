from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Lesson2.models import Base, Category, Subcategory, Product, City, Store, Special_offer
import requests
import json


class MarketDB:
    def __init__(self, base, db_url):
        engine = create_engine(db_url)
        base.metadata.create_all(engine)
        session_db = sessionmaker(bind=engine)
        self.__session = session_db()

    @property
    def session(self):
        return self.__session


class Loader:
    def __init__(self, mdb, url: str):
        self.__mdb = mdb
        self.__url = url
        self.__headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': '*/*'}

    def __load_categories(self, url: str):
        req = requests.get(url + 'categories/', headers=self.__headers)
        categories = json.loads(req.text)
        result = []
        for category in categories:
            result.append(Category(category['parent_group_code'], category['parent_group_name']))
        return result

    def __load_subcategories(self, url: str, category):
        url = url + 'categories/' + category.code + '/'
        req = requests.get(url, headers=self.__headers)
        subcategories = json.loads(req.text)
        result = []
        for subcategory in subcategories:
            result.append(Subcategory(subcategory['group_code'], subcategory['group_name'], category))
        return result

    def __load_products(self, url: str, category, subcategory):
        offer_url = url + 'special_offers/?store=&records_per_page=20&page=1&categories=' + subcategory.code
        result = []
        while offer_url != '':
            req = requests.get(offer_url, headers=self.__headers)
            offers = json.loads(req.text)
            products = offers['results']
            for prod in products:
                prod_url = url + 'special_offers/' + str(prod['id']) + '/'
                req_p = requests.get(prod_url, headers=self.__headers)
                product = json.loads(req_p.text)['product']
                result.append(Product(
                    product['plu'],
                    product['name'], category, subcategory,
                    prod['img_link'] if prod['img_link'] else '',
                    product['brand'],
                    product['country'],
                    product['weight'],
                    product['ingredients'],
                    product['protein'],
                    product['fat'],
                    product['carbohydrate'],
                    product['calories'],
                    product['shelf_life'],
                    product['remaining_shelf_life'],
                    product['package_type'],
                    product['measure_type']))
            offer_url = offers['next'] if offers['next'] else ''
        return result

    def __load_cities(self, url: str):
        # Загружаем не все магазины, а только несколько Москва, Питер, Звенигород
        cities = [1815, 1843, 1814]
        result = []
        for city in cities:
            req = requests.get(url + str(city), headers=self.__headers)
            city = json.loads(req.text)
            result.append(City(city['id'], city['name']))
        return result

    def __load_stores(self, url: str, city):
        # Загружаем не все магазины, а только несколько Москва, Питер, Звенигород
        cities = {'1814': '55.72706747773293,37.53581500463867,55.779344931814315,37.709192995361335',
                  '1843': '59.915686512824145,30.228946004638654,59.96219912218582,30.402323995361296',
                  '1815': '55.70352264276648,36.76863600463865,55.75583176091362,36.942013995361314'}
        result = []
        req = requests.get(url + 'stores/?bbox=' + str(cities[str(city.city_id)]), headers=self.__headers)
        stores = json.loads(req.text.replace('callback(', '').replace(');', ''))['data']['features']
        for store in stores:
            result.append(Store(
                store['id'],
                store['sap_code'],
                store['properties']['type'],
                store['properties']['city_id'],
                store['properties']['phone'],
                store['properties']['address'],
                store['properties']['city_name'],
                store['properties']['work_start_time'],
                store['properties']['work_end_time'],
                store['properties']['is_24h'],
                store['properties']['state'],
                city
            ))
        return result

    def __find_item(self, items, name):
        for item in items:
            if item.name == name:
                return item
        return None

    def __load_offers(self, url: str, store, categories, subcategories):
        offer_url = url + 'special_offers/?store=' + str(store.sap_code) + '&records_per_page=20&page=1'
        while offer_url != '':
            req = requests.get(offer_url, headers=self.__headers)
            offers = json.loads(req.text)
            products = offers['results']
            for prod in products:
                try:
                    prod_url = url + 'special_offers/' + str(prod['id']) + '/?store=' + str(store.sap_code)
                    req_p = requests.get(prod_url, headers=self.__headers)
                    offer = json.loads(req_p.text)

                    product = offer['product']
                    category = self.__find_item(categories, product['group']['parent_group_name'])
                    subcategory = self.__find_item(subcategories, product['group']['group_name'])
                    product_result = Product(
                        product['plu'],
                        product['name'], category, subcategory,
                        prod['img_link'] if prod['img_link'] else '',
                        product['brand'],
                        product['country'],
                        product['weight'],
                        product['ingredients'],
                        product['protein'],
                        product['fat'],
                        product['carbohydrate'],
                        product['calories'],
                        product['shelf_life'],
                        product['remaining_shelf_life'],
                        product['package_type'],
                        product['measure_type'])

                    self.__mdb.session.add(Special_offer(
                        offer['id'],
                        offer['name'],
                        offer['promo']['id'],
                        offer['promo']['date_begin'],
                        offer['promo']['date_end'],
                        offer['promo']['type'],
                        offer['promo']['description'],
                        offer['promo']['kind'],
                        offer['promo']['expired_at'],
                        float(offer['current_prices']['price_reg__min']),
                        float(offer['current_prices']['price_promo__min']),
                        offer['store_name'],
                        store,
                        product_result))
                    self.__mdb.session.commit()
                except Exception:
                    print('Error __load_offers')

            offer_url = offers['next'] if offers['next'] else ''

    def load(self):
        categories = self.__load_categories(self.__url)
        subcategories = []
        products = []
        for category in categories:
            subs = self.__load_subcategories(self.__url, category)
            subcategories.extend(subs)
        self.__mdb.session.add_all(subcategories)
        self.__mdb.session.commit()

        cities = self.__load_cities('https://5ka.ru/api/v1/cities/')
        stores = []
        for city in cities:
            stores.extend(self.__load_stores(self.__url, city))
        self.__mdb.session.add_all(stores)
        self.__mdb.session.commit()

        for store in stores:
            self.__load_offers(self.__url, store, categories, subcategories)


if __name__ == '__main__':
    db_url = 'mysql+pymysql://root:***@localhost/marketplace'
    db = MarketDB(Base, db_url)

    market = Loader(db, 'https://5ka.ru/api/v2/')
    market.load()
