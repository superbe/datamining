from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from Lesson4.avitolog import settings
from Lesson4.avitolog.spiders.avito import AvitoSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(AvitoSpider)
    process.start()
