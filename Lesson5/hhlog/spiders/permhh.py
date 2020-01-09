# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from Lesson5.hhlog.items import HhlogItem
from scrapy.loader import ItemLoader
from datetime import datetime


class PermhhSpider(scrapy.Spider):
    name = 'permhh'
    allowed_domains = ['perm.hh.ru']
    # Ставим регион 1317 (Пермский край) и указывает фильтровать вакансии для которых указан оклад only_with_salary=true
    start_urls = ['https://perm.hh.ru/search/vacancy?area=1317&only_with_salary=true']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath(
            '//div[contains(@data-qa, "pager-block")]/a[contains(@data-qa, "pager-next")]/@href').extract_first()
        vacancies = response.xpath(
            '//span[contains(@class, "g-user-content")]/a[contains(@data-qa, "vacancy-serp__vacancy-title")]/@href').extract()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

        for vacancy in vacancies:
            yield response.follow(vacancy[18:], callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        item = ItemLoader(HhlogItem(), response)

        item.add_value('url', response.url)
        item.add_value('parse_date', datetime.now())
        item.add_xpath('title', '//h1[contains(@data-qa, "vacancy-title")]/text()')
        item.add_xpath('salary',
                       '//div[contains(@class, "vacancy-title ")]/p[contains(@class, "vacancy-salary")]/text()')
        item.add_xpath('organisation',
                       '//p[contains(@class, "vacancy-company-name-wrapper")]/a[contains(@class, "vacancy-company-name")]/span[contains(@itemprop, "name")]/text()')
        item.add_xpath('organisation_url',
                       '//p[contains(@class, "vacancy-company-name-wrapper")]/a[contains(@class, "vacancy-company-name")]/@href')
        item.add_xpath('description', '//div[contains(@data-qa, "vacancy-description")]')

        yield item.load_item()
