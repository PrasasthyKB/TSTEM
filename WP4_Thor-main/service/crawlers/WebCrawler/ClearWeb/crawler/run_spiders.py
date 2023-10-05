import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from crawler.spiders import sitemap_spider, ache_spider

settings = get_project_settings()
runner = CrawlerRunner(settings)

configure_logging()
runner.crawl(sitemap_spider.SitemapSpider)
runner.crawl(ache_spider.AcheSpider)
d = runner.join()
d.addBoth(lambda _: reactor.stop())
reactor.run()
