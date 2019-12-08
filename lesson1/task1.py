# ==============================================================================
# Методы сбора и обработки данных из сети Интернет
# Урок 1. Основы клиент-серверного взаимодействия. Парсинг API
# Задание 1.
#
# Исполнитель: Евгений Бабарыкин
#
# Посмотреть документацию к API GitHub, разобраться как вывести список
# репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.
# ==============================================================================

import requests
import json

username = input('Введите логин пользователя: ')

if not username:
    username = 'superbe'

service = f'https://api.github.com/users/{username}/repos'

if not username:
    username = 'superbe'

headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
           'Accept': 'application/vnd.github.nebula-preview+json'}

req = requests.get(service, headers=headers)

data = json.loads(req.text)

print(data)

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)
