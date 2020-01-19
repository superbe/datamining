# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
from Lesson6.instalog.settings import mongo_client


class InstalogPipeline(object):
    def process_item(self, item, spider):
        data_base = mongo_client[spider.name]
        collection = data_base[type(item).__name__]
        item.update({'parse_date': datetime.now()})
        collection.insert(item)
        return item
