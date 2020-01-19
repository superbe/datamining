from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from Lesson5.hhlog import settings
from Lesson5.hhlog.spiders.permhh import PermhhSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(PermhhSpider)
    process.start()
