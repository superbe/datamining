# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst


class InstalogItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    parse_date = scrapy.Field(output_processor=TakeFirst())
    insta_id = scrapy.Field(output_processor=TakeFirst())
    username = scrapy.Field(output_processor=TakeFirst())
    full_name = scrapy.Field(output_processor=TakeFirst())
    profile_pic_url = scrapy.Field(output_processor=TakeFirst())


class InstagramUserProfile(InstalogItem):
    pass


class InstagramUserFollowers(InstalogItem):
    pass


class InstagramUserFollowing(InstalogItem):
    pass
