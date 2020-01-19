# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
import re

regex_html = re.compile(r'(\<(/?[^>]+)>)')
regex_s = re.compile(r'\s+')


def clear_description(value):
    return regex_s.sub(' ', regex_html.sub('', value)).strip()


class HhlogItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    parse_date = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(input_processor=MapCompose(clear_description), output_processor=TakeFirst())
    description = scrapy.Field(input_processor=MapCompose(clear_description), output_processor=TakeFirst())
    salary = scrapy.Field(input_processor=MapCompose(clear_description), output_processor=TakeFirst())
    organisation = scrapy.Field(input_processor=MapCompose(clear_description), output_processor=TakeFirst())
    organisation_url = scrapy.Field(output_processor=TakeFirst())
