# -*- coding: utf-8 -*-

import scrapy
import html2text
import re
import datetime
import requests
import url_normalize

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from crawler.items import CrawlerItem

IGNORED_EXTENSIONS = [
    # archives
    '7z', '7zip', 'bz2', 'rar', 'tar', 'tar.gz', 'xz', 'zip',

    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
    'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg', 'cdr', 'ico',

    # audio
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

    # video
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
    'm4a', 'm4v', 'flv', 'webm',

    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg',
    'odp',

    # other
    'css', 'pdf', 'exe', 'bin', 'rss', 'dmg', 'iso', 'apk', 'sig'
]


class AcheSpider(CrawlSpider):

    name = 'ache'
    seedfile = 'ache_seeds.txt'
    start_urls = [
    ]

    rules = (
        Rule(LxmlLinkExtractor(allow=(), deny_extensions=IGNORED_EXTENSIONS),
             callback="parse_item", follow=True),
    )
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    def __init__(self, *a, **kw):
        super(AcheSpider, self).__init__(*a, **kw)
        with open('ache_seeds.txt') as f:
            self.start_urls.extend([url.strip() for url in f.readlines()])
        #self.validate_urls(self.start_urls, self.seedfile)
            
    def parse_item(self, response):
        hxs = Selector(response)
        item = CrawlerItem()
        item['url'] = response.url
        item['server_header'] = str(response.headers)
        title_list = hxs.xpath('//title/text()').extract()
        h1_list = hxs.xpath("//h1/text()").extract()
        item['h1'] = " ".join(h1_list)
        h2_list = hxs.xpath("//h2/text()").extract()
        item['h2'] = " ".join(h2_list)
        title = ' '.join(title_list)
        item['title'] = title
        body_text = self.html2string(response)
        item['text'] = body_text

        item['spider_name'] = self.name
        item['date_inserted'] = str(
            datetime.datetime.now().replace(microsecond=0))
        return item

    def detect_encoding(self, response):
        return response.headers.encoding or "utf-8"

    def html2string(self, response):
        """HTML 2 string converter. Returns a string."""
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        encoding = self.detect_encoding(response)
        decoded_html = response.body.decode(encoding, 'ignore')
        string = converter.handle(decoded_html)
        return string
    def validate_urls(self, start_urls,seedfile):
        bad_url_file = 'ache_fault_urls.txt'
        bad_urls = []
        if not seedfile:
                print("File is empty or could not be read.")
        with open(seedfile, "w") as file:
            for url in start_urls:
                try:
                    response = requests.get(url.strip())
                    if response.status_code == 200:
                        file.write(url)
                    else:
                        bad_urls.append(url)
                except:
                    bad_urls.append(url)

        if bad_urls:
            with open(bad_url_file, "w") as file:
                for url in bad_urls:
                    file.write(url)
            print(f"The list of bad URLs has been saved to {bad_url_file}")
