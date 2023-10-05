# -*- coding: utf-8 -*-

import scrapy
import html2text
import re
import datetime

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


class WikiSpider1(CrawlSpider):

    name = 'wiki1'

    allowed_domains = ["onion"]
    start_urls = [
        "http://paavlaytlfsqyvkg3yqj7hflfg5jw2jdg2fgkza5ruf6lplwseeqtvyd.onion"
    ]

    rules = (
        Rule(
            LxmlLinkExtractor(
                allow=(),
                deny_extensions=IGNORED_EXTENSIONS),
            callback="parse_item",
            follow=True),
    )

    def parse_item(self, response):

        # #i = response.xpath('//h1/@class').extract()[0]
        # #i['name'] = response.xpath('//div[@id="name"]').extract()
        # #i['description'] = response.xpath('//div[@id="description"]').extract()
        # f = open("/Users/laveeshrohra/Documents/Workspace/checkPolipo.txt", "w+")
        # f.write("class = %s" % (response.body))
        # f.close()

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
        words = self.extract_words(body_text)
        item['text'] = title + " " + " ".join(words)
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

    def extract_words(self, html_string):
        """Stems and counts the words. Works only in English!"""
        string_list = re.split(r' |\n|#|\*', html_string)
        # Cut a word list that is larger than 10000 words
        if len(string_list) > 10000:
            string_list = string_list[0:10000]
        words = []
        for word in string_list:
            # Word must be longer than 0 letter
            # And shorter than 45
            # The longest word in a major English dictionary is
            # Pneumonoultramicroscopicsilicovolcanoconiosis (45 letters)
            if len(word) > 0 and len(word) <= 45:
                words.append(word)
        return words
