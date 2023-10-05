import logging
import scrapy.dupefilters
import pymongo

class MongoDBFilter(scrapy.dupefilters.RFPDupeFilter):

    def __init__(self, path=None,debug: bool = False,*,fingerprinter=None,):
        self.mongo_client = pymongo.MongoClient("mongodb://Crawler:CrawlerIsAwesome@mongodb")
        self.mongo_db = self.mongo_client['scrapy']
        self.mongo_collection = self.mongo_db['clearweb_crawler']

        result = self.mongo_collection.create_index([('rfp', pymongo.ASCENDING)],unique=True)
        scrapy.dupefilters.RFPDupeFilter.__init__(self, path,debug)

    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        try:
            result = self.mongo_collection.insert_one({"rfp":fp})
            return False

        except pymongo.errors.DuplicateKeyError: 
            return True
