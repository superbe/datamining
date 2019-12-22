from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient


class Loader:
    def __init__(self, url: str, db_url: str, db_name: str, collection_name):
        self.__url = url
        self.__client = MongoClient(db_url)
        self.__db = self.__client[db_name]
        self.__collection = self.__db[collection_name]

    def __get_count_pages(self, url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        return int(soup.find('li', attrs={'class': 'page'}).previousSibling.text)

    def __get_pages_url(self, url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        a_tags = soup.find_all('a', attrs={'class': 'post-item__title h3 search_text'})
        result = []
        for a in a_tags:
            result.append(self.__url + a['href'])
        return result

    def __get_post(self, url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('h1', attrs={'class': 'blogpost-title text-left text-dark m-t-sm'}).string
        date = soup.find('time', attrs={'class': 'text-md text-muted m-r-md'})['datetime'][:10]
        author = soup.find('div', attrs={'itemprop': 'author'}).string
        self.__collection.insert_one({'title': title, 'url': url, 'date': date, 'author': author})

    def load(self):
        count = self.__get_count_pages(self.__url + '/posts/')
        pages_urls = [self.__url + '/posts?page=' + str(i) for i in range(count + 1)]
        article_pages = []
        for url in pages_urls:
            article_pages.extend(self.__get_pages_url(url))
        for article_url in article_pages:
            self.__get_post(article_url)


if __name__ == '__main__':
    loader = Loader('https://geekbrains.ru', 'mongodb://localhost:27017/', 'geekbrains', 'posts')
    loader.load()
