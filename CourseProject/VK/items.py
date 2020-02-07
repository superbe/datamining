# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, ChainMap


def format_chain(value):
    return f'https://vk.com/{value}'


class VkItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    parse_date = scrapy.Field(output_processor=TakeFirst())
    # Первый пользователь.
    person_a = scrapy.Field(output_processor=TakeFirst())
    # Второй пользователь.
    person_b = scrapy.Field(output_processor=TakeFirst())
    # Цепочка друзей.
    chain = scrapy.Field(input_processor=MapCompose(format_chain))
