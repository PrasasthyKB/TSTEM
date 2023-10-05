# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.item import Field, Item


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    domain = Field()
    url = Field()
    tor2web_url = Field()
    title = Field()
    h1 = Field()
    h2 = Field()
    server_header = Field()
    text = Field()
    date_inserted = Field()
    spider_name = Field()
