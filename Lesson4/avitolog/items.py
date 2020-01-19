# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AvitologItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    attributes = scrapy.Field()
    price = scrapy.Field()
