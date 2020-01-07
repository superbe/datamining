from sqlalchemy import (Table, Column, ForeignKey, String, Integer, VARCHAR, INT, BOOLEAN, FLOAT, TIMESTAMP, TIME)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, time

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    id = Column(INT, primary_key=True, autoincrement=True)
    code = Column(VARCHAR(5), unique=True)
    name = Column(VARCHAR(255), unique=True)

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name


class Subcategory(Base):
    __tablename__ = 'subcategories'
    id = Column(INT, primary_key=True, autoincrement=True)
    code = Column(VARCHAR(6), unique=True)
    name = Column(VARCHAR(255))
    __category = Column('category_id', INT, ForeignKey('categories.id'))
    category = relationship('Category', backref='subcategories')

    # def __init__(self, code: str, name: str, category):
    def __init__(self, code: str, name: str, category):
        self.code = code
        self.name = name
        self.category = category


class Product(Base):
    __tablename__ = 'products'
    id = Column(INT, primary_key=True, autoincrement=True)
    plu = Column(INT)
    name = Column(VARCHAR(255))
    __category = Column('category_id', INT, ForeignKey('categories.id'))
    category = relationship('Category', backref='products')
    __subcategory = Column('subcategory_id', INT, ForeignKey('subcategories.id'))
    subcategory = relationship('Subcategory', backref='products')
    img = Column(VARCHAR(255))
    brand = Column(VARCHAR(255))
    country = Column(VARCHAR(255))
    weight = Column(VARCHAR(255))
    ingredients = Column(VARCHAR(2048))
    protein = Column(INT)
    fat = Column(INT)
    carbohydrate = Column(INT)
    calories = Column(INT)
    shelf_life = Column(INT)
    remaining_shelf_life = Column(INT)
    package_type = Column(INT)
    measure_type = Column(INT)

    def __init__(self, plu: int, name: str, category, subcategory, img: str, brand: str, country: str, weight: str,
                 ingredients: str, protein: int, fat: int, carbohydrate: int, calories: int, shelf_life: int,
                 remaining_shelf_life: int, package_type: int, measure_type: int):
        self.plu = plu
        self.name = name
        self.category = category
        self.subcategory = subcategory
        self.img = img
        self.brand = brand
        self.country = country
        self.weight = weight
        self.ingredients = ingredients
        self.protein = protein
        self.fat = fat
        self.carbohydrate = carbohydrate
        self.calories = calories
        self.shelf_life = shelf_life
        self.remaining_shelf_life = remaining_shelf_life
        self.package_type = package_type
        self.measure_type = measure_type


class City(Base):
    __tablename__ = 'cities'
    id = Column(INT, primary_key=True, autoincrement=True)
    city_id = Column(INT)
    name = Column(VARCHAR(255), unique=True)

    def __init__(self, city_id: int, name: str):
        self.city_id = city_id
        self.name = name


class Store(Base):
    __tablename__ = 'stores'
    id = Column(INT, primary_key=True, autoincrement=True)
    store_id = Column(INT)
    sap_code = Column(VARCHAR(255))
    type = Column(VARCHAR(255))
    phone = Column(VARCHAR(255))
    address = Column(VARCHAR(255))
    city_name = Column(VARCHAR(255))
    work_start_time = Column(TIME)
    work_end_time = Column(TIME)
    is_24h = Column(BOOLEAN)
    state = Column(VARCHAR(255))
    __city = Column('city_id', INT, ForeignKey('cities.id'))
    city = relationship('City', backref='stores')

    def __init__(self, store_id: int, sap_code: str, type: str, city_id: str, phone: str, address: str, city_name: str,
                 work_start_time: str, work_end_time: str, is_24h: bool, state: str, city):
        self.store_id = store_id
        self.sap_code = sap_code
        self.type = type
        self.phone = phone
        self.address = address
        self.city_name = city_name
        self.work_start_time = work_start_time
        self.work_end_time = work_end_time
        self.is_24h = is_24h
        self.state = state
        self.city = city


class Special_offer(Base):
    __tablename__ = 'offers'
    id = Column(INT, primary_key=True, autoincrement=True)
    offer_id = Column(INT)
    name = Column(VARCHAR(255))
    promo_id = Column(INT)
    promo_date_begin = Column(TIMESTAMP)
    promo_date_end = Column(TIMESTAMP)
    promo_type = Column(VARCHAR(255))
    promo_description = Column(VARCHAR(255))
    promo_kind = Column(VARCHAR(255))
    promo_expired_at = Column(INT)
    price_reg__min = Column(FLOAT)
    price_promo__min = Column(FLOAT)
    store_name = Column(VARCHAR(255))
    __store = Column('store_id', INT, ForeignKey('stores.id'))
    store = relationship('Store', backref='offers')
    __product = Column('product_id', INT, ForeignKey('products.id'))
    product = relationship('Product', backref='offers')

    # def __init__(self, code: str, name: str, category):
    def __init__(self, offer_id: int, name: str, promo_id: int, promo_date_begin: str,
                 promo_date_end: str, promo_type: str, promo_description: str, promo_kind: str, promo_expired_at: int,
                 price_reg__min: float, price_promo__min: float, store_name: str, store, product):
        self.offer_id = offer_id
        self.name = name
        self.promo_id = promo_id
        self.promo_date_begin = datetime.strptime(promo_date_begin, '%Y-%m-%d')
        self.promo_date_end = datetime.strptime(promo_date_end, '%Y-%m-%d')
        self.promo_type = promo_type
        self.promo_description = promo_description
        self.promo_kind = promo_kind
        self.promo_expired_at = promo_expired_at
        self.price_reg__min = price_reg__min
        self.price_promo__min = price_promo__min
        self.store_name = store_name
        self.store = store
        self.product = product
