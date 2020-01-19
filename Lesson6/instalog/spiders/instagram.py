# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from Lesson6.instalog.items import InstagramUserProfile, InstagramUserFollowers, InstagramUserFollowing


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
    user_data_hash_followers = 'c76146de99bb02f6415203be841dd25a'
    user_data_hash_following = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.user_login, 'password': self.user_password},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        for user in self.parse_user:
            yield response.follow(f'/{user}', callback=self.userdata_parse, cb_kwargs={'username': user})

    def userdata_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            'include_reel': True,
            'fetch_mutual': True,
            'first': 9999999999
        }
        user_variables = {
            'user_id': "11751898",
            'include_chaining': True,
            'include_reel': True,
            'include_suggested_users': False,
            'include_logged_out_extras': False,
            'include_highlight_reels': True,
            'include_related_profiles': True
        }
        url_user_profile = f'{self.graphql_url}query_hash={self.user_data_hash}&variables={json.dumps(user_variables)}'
        yield response.follow(url_user_profile, callback=self.user_profile_data_parse, cb_kwargs={'username': username})
        url_followers = f'{self.graphql_url}query_hash={self.user_data_hash_followers}&variables={json.dumps(variables)}'
        yield response.follow(url_followers, callback=self.followers_data_parse, cb_kwargs={'username': username})
        url_following = f'{self.graphql_url}query_hash={self.user_data_hash_following}&variables={json.dumps(variables)}'
        yield response.follow(url_following, callback=self.following_data_parse, cb_kwargs={'username': username})

    def user_profile_data_parse(self, response: HtmlResponse, username):
        item = ItemLoader(InstagramUserProfile(), response)
        item.add_value('url', response.url)
        user_profile = json.loads(response.text)['data']['user']['reel']['user']
        item.add_value('insta_id', user_profile['id'])
        item.add_value('username', user_profile['username'])
        item.add_value('full_name', '')
        item.add_value('profile_pic_url', user_profile['profile_pic_url'])
        print(item.load_item())
        yield item.load_item()

    def followers_data_parse(self, response: HtmlResponse, username):
        users_data = json.loads(response.text)['data']['user']['edge_followed_by']['edges']
        for user_item in users_data:
            user_data = user_item['node']
            item = ItemLoader(InstagramUserFollowers(), response)
            item.add_value('url', response.url)
            item.add_value('insta_id', user_data['id'])
            item.add_value('username', user_data['username'])
            item.add_value('full_name', user_data['full_name'])
            item.add_value('profile_pic_url', user_data['profile_pic_url'])
            print(item.load_item())
            yield item.load_item()

    def following_data_parse(self, response: HtmlResponse, username):
        users_data = json.loads(response.text)['data']['user']['edge_follow']['edges']
        for user_item in users_data:
            user_data = user_item['node']
            item = ItemLoader(InstagramUserFollowing(), response)
            item.add_value('url', response.url)
            item.add_value('insta_id', user_data['id'])
            item.add_value('username', user_data['username'])
            item.add_value('full_name', user_data['full_name'])
            item.add_value('profile_pic_url', user_data['profile_pic_url'])
            print(item.load_item())
            yield item.load_item()

    def fetch_csrf_token(self, text):
        return self.regex_token.search(text).group().split(':').pop().replace('"', '')

    def fetch_user_id(self, text, username):
        return json.loads(re.search(r'{\"id\":\"\d+\",\"username\":\"%s\"}' % username, text).group()).get('id')
