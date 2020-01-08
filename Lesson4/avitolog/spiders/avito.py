# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from Lesson4.avitolog.items import AvitologItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = [f'https://www.avito.ru/kazan/kvartiry/prodam?p={i}' for i in range(1, 101)]

    def parse(self, response: HtmlResponse):
        urls = response.xpath(
            '//h3[contains(@data-marker, "item-title")]/a[contains(@itemprop, "url")]/@href').extract()
        for ad_url in urls:
            yield response.follow(ad_url, callback=self.ad_parse)

    def ad_parse(self, response: HtmlResponse):
        attributes = {}
        keys = response.xpath(
            '//ul[contains(@class, "item-params-list")]/li[contains(@class, "item-params-list-item")]/span[contains(@class, "item-params-label")]/text()').extract()

        values = response.xpath(
            '//ul[contains(@class, "item-params-list")]/li[contains(@class, "item-params-list-item")]/text()').extract()

        for i in range(len(keys)):
            attributes[keys[i]] = values[2 * i + 1]

        yield AvitologItem(
            title=response.xpath('//h1[contains(@class, "title-info-title")]/span[contains(@class, "title-info-title-text")]/text()').extract_first(),
            attributes=attributes,
            price=response.xpath('//div[contains(@id, "price-value")]/span/span[contains(@itemprop, "price")]/@content').extract_first(),
        )
