# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
# https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables={"id":"11751898","include_reel":true,"fetch_mutual":false,"first":24}
# https://www.instagram.com/graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables={"id":"11751898","include_reel":true,"fetch_mutual":true,"first":190}

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['http://www.instagram.com/']
    regex_token = re.compile(r'\"csrf_token\":\"\w+\"')
    user_login = input('Введите логин: ')
    user_password = input('Введите пароль: ')
    login_link = 'http://www.instagram.com/accounts/login/ajax/'
    parse_user = ['gefestart']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    user_data_hash = 'c9100bf9110dd6361671f113dd02e7d6'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.user_login, 'password': self.user_password},
            headers={'X-CSRFToken': csrf_token}
        )
        print(1)

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        for user in self.parse_user:
            yield response.follow(f'/{user}', callback=self.userdata_parse, cb_kwargs={'username': user})

    def userdata_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        print(1)

    def fetch_csrf_token(self, text):
        return self.regex_token.search(text).group().split(':').pop().replace('"', '')

    def fetch_user_id(self, text, username):
        return json.loads(re.search(r'{\"id\":\"\d+\",\"username\":\"%s\"}' % username,  text).group()).get('id')
