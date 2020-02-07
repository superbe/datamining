# Методы сбора и обработки данных из сети Интернет
# Итоговый проект
#
# Курсовая работа:
# Рессурс на выбор или VK, или FB
#
# Ваша задача на старте паука принять 2 сслыки на странички пользователей (людей)
# Найти самую короткую цепочку рукопожатий именно составля ее из общих друзей
# https://ru.wikipedia.org/wiki/Теория_шести_рукопожатий
#
# В результате у вас должна быть база данных в которой:
# {
# "person_a": "url", # ссылка на персону A
# "person_b":"url", # ссылка на персону B
# chain: [<url>, <url> ....] # цепочка (список) из ссылок
# }

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from CourseProject.VK import settings
from CourseProject.VK.spiders.vk import VkSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(VkSpider)
    process.start()
