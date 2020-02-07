# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.http import HtmlResponse
from CourseProject.VK.items import VkItem
from scrapy.loader import ItemLoader


class VkSpider(scrapy.Spider):
    """
    Паук vk.com
    Обходим друзей по следующей схеме. Сначала загружаем данные профиля первого пользователя. На первой итерации
    загружаем друзей первого пользователя, на второй итерации загружаем друзей друзей первого пользователя и так до тех
    пор пока в итерации не попадет второй пользователь. После того как второй пользоватлеь обнаружен на очередной
    итерации в списке друзей завершаем поиск, получаем данные профиля второго пользователя и выстраиваем цепочку друзей.
    При обходе в отдельный список сохраняем уже обойдённых пользователей, чтобы наш поиск не зациклился и не обрабатывал
    бы одного и того же друга дважды. Здесь косые - связи, 0 - друзья не попавшие в цепочку, X - друзья попавшие
    в цепочку, 1 - первый пользователь, 2 - конечный пользователь.

    1 2 3 4 (итерации)

          0
         /
        0-0
       /
      X-X-2
     / \ /
    1-X-X-0
     \ / \
      X-0-0
       \ /
        0-0
         \
          0
    """
    name = 'vk'
    allowed_domains = ['vk.com', 'api.vk.com', 'oauth.vk.com', 'm.vk.com']
    start_urls = [
        'https://oauth.vk.com/authorize?client_id=7287774&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.52']
    client_id = 7287774
    login_link = 'https://login.vk.com/?act=login&soft=1'
    oauth_link = 'https://oauth.vk.com/authorize?client_id=7287774&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.52'
    code_form_link = 'https://m.vk.com'
    users_get_link = 'https://api.vk.com/method/users.get'
    friends_get_link = 'https://api.vk.com/method/friends.get'
    site_url = 'https://vk.com/'
    stopped = False
    stop_list = []

    def parse(self, response: HtmlResponse):
        """
        Обработать форму авторизации. Точка входа в парсинг vk.com.
        :param response: ответ запроса страницы авторизации.
        """
        # Авторизуемся на странице.
        user_email = input('Введите email: ')
        user_password = input('Введите пароль: ')

        # Готовим данные для формы.
        ip_h = response.xpath(
            '//div[contains(@class, "oauth_form_login")]/input[contains(@name, "ip_h")]/@value').extract_first()
        lg_h = response.xpath(
            '//div[contains(@class, "oauth_form_login")]/input[contains(@name, "lg_h")]/@value').extract_first()
        _origin = response.xpath(
            '//div[contains(@class, "oauth_form_login")]/input[contains(@name, "_origin")]/@value').extract_first()
        to = response.xpath(
            '//div[contains(@class, "oauth_form_login")]/input[contains(@name, "to")]/@value').extract_first()
        expire = response.xpath(
            '//div[contains(@class, "oauth_form_login")]/input[contains(@name, "expire")]/@value').extract_first()
        yield scrapy.FormRequest(
            self.login_link,
            method='POST',
            callback=self.user_parse,
            formdata={
                'ip_h': ip_h,
                'lg_h': lg_h,
                '_origin': _origin,
                'to': to,
                'expire': expire,
                'email': user_email,
                'pass': user_password
            }
        )

    def user_parse(self, response: HtmlResponse):
        """
        Обработать форму ввода кода подтверждения авторизации.
        :param response: ответ запроса ввода формы авторизации.
        """
        # Вводим проверочный код доступа.
        user_code = input('Введите код: ')
        action = response.xpath('//div[contains(@class, "form_item fi_fat")]/form/@action').extract_first()
        url = f'{self.code_form_link}{action}'
        yield scrapy.FormRequest(
            url,
            method='POST',
            callback=self.code_parse,
            formdata={
                'code': user_code,
                'remember': '1'
            }
        )

    def code_parse(self, response: HtmlResponse):
        """
        Обработать ответ сервера запроса авторизации.
        :param response: ответ завпроса авторизации.
        """
        # Получили токен авторизации
        token = response.request.url.split('#')[-1].split('&')[0].split('=')[-1]
        #  Вместо токена вернулась капча.
        if token == 'authcheck_code':
            # Формируем данные для капчи.
            img_src = response.xpath(
                '//form/div[contains(@class, "fi_row")]/img[contains(@class, "captcha_img")]/@src').extract_first()
            captcha_url = f'{self.code_form_link}{img_src}'
            action = response.xpath('//form/@action').extract_first()
            action_url = f'{self.code_form_link}{action}'
            captcha_sid = response.xpath('//form/input[contains(@name, "captcha_sid")]/@value').extract_first()
            captcha_code = response.xpath('//form/input[contains(@name, "code")]/@value').extract_first()
            captcha_remember = response.xpath('//form/input[contains(@name, "remember")]/@value').extract_first()
            yield response.follow(captcha_url, callback=self.captcha_parse,
                                  cb_kwargs={'action_url': action_url, 'captcha_sid': captcha_sid,
                                             'captcha_code': captcha_code,
                                             'captcha_remember': captcha_remember})
        else:
            #  Токен получен
            # Вводим ссылки на странички пользователей.
            first_user_ids = input('Введите url первого пользователя: ').split('/')[-1].strip()
            second_user_ids = input('Введите url второго пользователя: ').split('/')[-1].strip()
            first_user_url = f'{self.users_get_link}?user_ids={first_user_ids}&fields=screen_name&access_token={token}&v=5.89'
            yield response.follow(first_user_url, callback=self.user_profile_parse,
                                  cb_kwargs={'token': token, 'current_user': first_user_ids,
                                             'first_user': first_user_ids,
                                             'second_user': second_user_ids, 'chain': ''})

    def captcha_parse(self, response: HtmlResponse, action_url, captcha_sid, captcha_code, captcha_remember):
        """
        Загрузить капчу. Отдельный паплайн создавать нецелесообразно, так как надо встроить загрузку изображения капчи в
        общую последоватльеность процесса авторизации.
        :param response: ответ запроса изображения капчи.
        :param action_url: адрес формы ввода капчи.
        :param captcha_sid: идентификатор капчи для серверного представления.
        :param captcha_code: код капчи для серверного представления.
        :param captcha_remember: служебный параметр для серверного представления
        """
        # Вводим данные с капчи.
        with open('captcha.jpg', 'wb') as image:
            image.write(response.body)

        code = input('Введите код с капчи: ')
        yield scrapy.FormRequest(
            action_url,
            method='POST',
            callback=self.code_parse,
            formdata={
                'captcha_sid': captcha_sid,
                'code': captcha_code,
                'remember': captcha_remember,
                'captcha_key': code
            }
        )

    def user_profile_parse(self, response: HtmlResponse, token, current_user, first_user, second_user, chain):
        """
        Обработать загруженные данные пользователя.
        :param response: ответ запроса данных профиля пользователя.
        :param token: токен авторизации.
        :param current_user: запрашиваемый пользователь.
        :param first_user: первый пользователь для кого ищем общих друзей.
        :param second_user: второй пользователь для кого ищем общих друзей.
        :param chain: цепочка общих друзей для первого и второго пользователей.
        """
        if not self.stopped:
            try:
                if json.loads(response.text)['response'][0]['screen_name']:
                    # Если текущий пользователь оказался конечным (вторым) пользоватлем завершаем обход.
                    screen_name = json.loads(response.text)['response'][0]['screen_name']
                    user_id = json.loads(response.text)['response'][0]['id']
                    self.stop_list.append(user_id)
                    if second_user == screen_name:
                        # Останавливаем обход, так как нашли всю цепочку.
                        self.stopped = True
                        second_user_url = f'{self.users_get_link}?user_id={second_user}&fields=screen_name&access_token={token}&v=5.89'
                        yield response.follow(second_user_url, callback=self.second_user_profile_parse,
                                              cb_kwargs={'token': token, 'first_user': first_user,
                                                         'second_user': second_user,
                                                         'chain': chain})
                    else:
                        # Запрашиваем друзей текущего пользователя.
                        friends_url = f'{self.friends_get_link}?user_id={user_id}&fields=screen_name&access_token={token}&v=5.89'
                        yield response.follow(friends_url, callback=self.friends_parse,
                                              cb_kwargs={'token': token, 'first_user': first_user,
                                                         'second_user': second_user,
                                                         'chain': chain})

            except KeyError as e:
                # Обрабатываем ошибку на тот случай, если пользователь заблокирован или удален и данные по нему
                # не пришли. переходим к следующей итерации.
                print('Ошибка "KeyError"')

    def friends_parse(self, response: HtmlResponse, token, first_user, second_user, chain):
        """
        Получить друзей пользователя.
        :param response: Ответ сервера на запрос друзей пользователя.
        :param token: токен авторизации.
        :param first_user: первый пользователь для кого ищем общих друзей.
        :param second_user: второй пользователь для кого ищем общих друзей.
        :param chain: цепочка общих друзей для первого и второго пользователей.
        """
        if not self.stopped:
            try:
                if 'response' in json.loads(response.text):
                    items = json.loads(response.text)['response']['items']
                    # Проходим всех друзей текущего пользователя.
                    for item in items:
                        if 'screen_name' in item:
                            user_id = item['id']
                            if not user_id in self.stop_list:
                                screen_name = item['screen_name']
                                if chain == '':
                                    new_chain = screen_name
                                else:
                                    new_chain = chain + ',' + screen_name
                                user_url = f'{self.users_get_link}?user_id={user_id}&fields=screen_name&access_token={token}&v=5.89'
                                yield response.follow(user_url, callback=self.user_profile_parse,
                                                      cb_kwargs={'token': token, 'current_user': user_id,
                                                                 'first_user': first_user,
                                                                 'second_user': second_user, 'chain': new_chain})
            except KeyError as e:
                print('Ошибка "KeyError"')

    def second_user_profile_parse(self, response: HtmlResponse, token, first_user, second_user, chain):
        """
        Получить данные конечного пользовталея.
        :param response: Ответ сервера на запрос профиля конечного пользователя.
        :param token: токен авторизации.
        :param first_user: первый пользователь для кого ищем общих друзей.
        :param second_user: второй пользователь для кого ищем общих друзей.
        :param chain: цепочка общих друзей для первого и второго пользователей.
        """
        item = ItemLoader(VkItem(), response)
        item.add_value('url', response.url)
        item.add_value('person_a', f'{self.site_url}{first_user}')
        item.add_value('person_b', f'{self.site_url}{second_user}')
        chain_list = chain.split(',')[0:-1]
        item.add_value('chain', chain_list)
        yield item.load_item()
