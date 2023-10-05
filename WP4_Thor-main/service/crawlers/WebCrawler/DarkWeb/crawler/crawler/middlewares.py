# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
import random
import requests
import urllib.parse
from urllib.parse import urlsplit
from scrapy import signals
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class CrawlerSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware:
    def process_request(self, request, spider):
        ua = random.choice(spider.settings.get('USER_AGENT_LIST'))
        if ua:
            request.headers.setdefault('User-Agent', ua)

class NormalizeURIMiddleware:
    
    def process_request(self, request, spider):
        parsed_url = urllib.parse.urlparse(request.url)
        normalized_url = urllib.parse.urlunparse(
            (
                parsed_url.scheme.lower(),
                parsed_url.netloc.lower(),
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            )
        )
        request = request.replace(url=normalized_url)
        return None


class SpamIdentificationMiddleware:
    robots_cache = {}

    def process_request(self, request, spider):
        domain = urlsplit(request.url).netloc
        robots_url = "http://" + domain + "/robots.txt"
        
        # Check if we already have the robots.txt file for this domain in the cache
        if domain in self.robots_cache:
            robots_txt = self.robots_cache[domain]
        else:
            # If not, retrieve it from the website
            response = requests.get(robots_url, verify=True)
            if response.status_code == 200:
                robots_txt = response.text
                # Add the robots.txt file to the cache
                self.robots_cache[domain] = robots_txt
            else:
                # If the robots.txt file cannot be retrieved, continue crawling
                return request
        
        # Check if the current request is allowed by the website's robots.txt file
        if "Disallow: " + urlsplit(request.url).path in robots_txt:
            # If the URL is disallowed, don't crawl it and return None
            return None
        else:
            # If the URL is allowed, continue crawling
            return request


class CanonicalizationMiddleware:
    def process_response(self, request, response, spider):
        canonical_link = response.xpath('//link[@rel="canonical"]/@href').get()
        if canonical_link:
            # Use the canonical URL instead of the current URL
            request = request.replace(url=canonical_link)
            return request
        else:
            # No canonical link found, return the response as is
            return response
