# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import json
import hashlib
from collections import deque

from itemadapter import ItemAdapter

from scrapy.utils.project import get_project_settings

from kafka import KafkaProducer


class CrawlerPipeline:
    def __init__(self):
        """
        :type producer: kafka.producer.Producer
        :type topic: str or unicode
        """
        settings = get_project_settings()

        self.producer = KafkaProducer(bootstrap_servers=settings.get(
            "KAFKA_SERVER"), api_version=(0, 11, 15), batch_size=128)
        self.topic = settings.get("KAFKA_TOPIC")
        self.hashes = deque([], maxlen=100)


    def open_spider(self, spider):
        #self.file = open('items.jl', 'w')
        pass

    def close_spider(self, spider):
        # self.file.close()
        pass

    def process_item(self, item, spider):
        text_hash = hashlib.md5(item["text"].encode()).hexdigest()
        if text_hash not in self.hashes:
            self.hashes.append(text_hash)
            json_payload = json.dumps(dict(item))
            json_payload = str.encode(json_payload)
            self.producer.send(self.topic, json_payload)
            return item
