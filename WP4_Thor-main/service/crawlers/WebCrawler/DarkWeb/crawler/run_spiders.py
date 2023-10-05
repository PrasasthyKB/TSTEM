import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from crawler.spiders import ahmia_spider, wiki_spider1, wiki_spider2, wiki_spider3, wiki_spider4

settings = get_project_settings()
runner = CrawlerRunner(settings)

configure_logging()
runner.crawl(ahmia_spider.AhmiaSpider)
#runner.crawl(wiki_spider1.WikiSpider1)
#runner.crawl(wiki_spider2.WikiSpider2)
#runner.crawl(wiki_spider3.WikiSpider3)
#runner.crawl(wiki_spider4.WikiSpider4)
d = runner.join()
d.addBoth(lambda _: reactor.stop())
reactor.run()
