from bs4 import BeautifulSoup
import requests

start_url = 'https://geekbrains.ru/posts'

response = requests.get(start_url)

soup = BeautifulSoup(response.text, 'lxml')

print(soup.text)

class Loader


# if __name__ == '__main__':
