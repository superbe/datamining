# ==============================================================================
# Методы сбора и обработки данных из сети Интернет
# Урок 1. Основы клиент-серверного взаимодействия. Парсинг API
# Задание 2.
#
# Исполнитель: Евгений Бабарыкин
#
# Изучить список открытых API. Найти среди них любое, требующее авторизацию
# (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера
# записать в файл.
#
# Выбрал API для сайта OpenStreetMap
# https://www.programmableweb.com/api/openstreetmap
# Загрузим данные пользователя.
#
# ==============================================================================

import requests
import json
from xml.dom.minidom import parseString
from requests.auth import HTTPBasicAuth


def process_request(command, log, pas):
    request = requests.get(f'https://api.openstreetmap.org/api/0.6/user/{command}/',
                           auth=HTTPBasicAuth(log, pas))
    if request.status_code == 200:
        data = parseString(request.text)
        print(data)

        with open(f'openstreetmap_{command}.xml', 'w') as outfile:
            data.writexml(outfile)


login = input('Введите логин пользователя: ')
password = input('Введите пароль пользователя: ')
url = 'https://api.openstreetmap.org/'
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
           'Accept': 'application/vnd.github.nebula-preview+json'}

req = requests.get(url, auth=HTTPBasicAuth(login, password))

if req.status_code == 200:
    process_request('details', login, password)
    process_request('preferences', login, password)
    process_request('gpx_files', login, password)
